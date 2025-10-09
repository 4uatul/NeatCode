"""
Flask backend for the refactoring app. It serves the provided UI and exposes two API
endpoints for JSON refactors and file uploads. Requests are forwarded to an OpenAI-backed
engine that returns a specific JSON schema. A request without a valid API key will receive
an HTTP 503 Service Unavailable response.
"""

import os
from typing import Any
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
from dotenv import load_dotenv
from config import load_settings
from services.ai_client import invoke_refactor_engine

# Load settings and ensure the upload directory exists
load_dotenv(override=True)  # let .env replace any pre-set variable
settings = load_settings()
os.makedirs(settings.upload_dir, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.update(UPLOAD_FOLDER=settings.upload_dir, MAX_CONTENT_LENGTH=settings.max_bytes,)

# A frontend origin is the full site address that the browser treats as the page owner
# It is composed of scheme, host, and port, for example http://localhost:3000
# During local development the page usually runs on localhost with varying ports
# The entries below allow that while still locking production to your known origin(s)
allowed_origins = {settings.frontend_origin}

# Allow localhost by default; set FRONTEND_ALLOW_LOCALHOST=0 to disable
if os.getenv("FRONTEND_ALLOW_LOCALHOST", "1") == "1":
    # regex patterns match any localhost or 127.0.0.1 port
    allowed_origins.add(r"http://localhost:\d+")
    allowed_origins.add(r"http://127\.0\.0\.1:\d+")

CORS(app, resources={r"/api/*": {"origins": list(allowed_origins)}}, max_age=600,)


@app.get("/")
def home() -> str:
    """
    Serve the static UI from index.html.
    """
    return render_template("index.html")


@app.get("/health")
def get_health_status() -> Response:
    """
    Basic health check to help with deployments and monitoring. Responds with
    HTTP 200 and a body that says status ok

    """
    resp = jsonify(status="ok")
    resp.status_code = 200
    return resp


@app.post("/api/refactor")
def post_refactor_request() -> Response:
    """
    Accept a JSON or form payload with source code, language, and objectives
    (backward compatible with 'goals'). Returns {refactored_code, explanation}.
    """
    try:
        data: dict[str, Any] = request.get_json(silent=True) or {}
    except BadRequest:
        return jsonify(error="invalid JSON"), 400

    # If this endpoint is hit with form-data, merge minimal fields we care about.
    form_objectives = None
    if not data and request.form:
        data = request.form.to_dict(flat=True)  # single-value fields
        # support repeated fields: objectives=...&objectives=...
        form_objectives = request.form.getlist("objectives") or request.form.getlist("goals")

    source: str = (data.get("source") or "").strip()
    language: str = data.get("language", "python")

    def _normalize_objectives(v) -> list[str]:
        default = ["readability", "remove dead code", "style/PEP8"]
        if v is None:
            return default
        if isinstance(v, str):
            parts = [s.strip() for s in v.split(",") if s.strip()]
            return parts or default
        if isinstance(v, (list, tuple)):
            parts = [str(s).strip() for s in v if str(s).strip()]
            return parts or default
        return default

    raw_objectives = (data.get("objectives") or data.get("goals") or form_objectives
                      or ["readability", "remove dead code", "style/PEP8"])
    objectives: list[str] = _normalize_objectives(raw_objectives)

    if not source:
        return jsonify(error="'source' is required"), 400

    try:
        result = invoke_refactor_engine(source=source, language=language, goals=objectives)
        return jsonify(result), 200
    except RuntimeError as e:
        message = str(e)
        if "OPENAI_QUOTA_EXCEEDED" in message or "insufficient_quota" in message:
            status = 429
        elif "OPENAI_API_KEY is required" in message:
            status = 503
        elif "OPENAI_AUTH_ERROR" in message:
            status = 401
        else:
            status = 500
        return jsonify(error="refactor failed", detail=message), status
    except Exception as e:
        return jsonify(error="refactor failed", detail=str(e)), 500


@app.post("/api/upload")
def post_upload_request() -> Response:
    """
    Accept a multipart upload ('file') and optional 'language', run the refactor,
    and return the filename alongside the refactoring result.
    """
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        resp = jsonify(error="missing file")
        resp.status_code = 400
        return resp

    # Save to a safe path and then read the content for refactoring.
    filename = secure_filename(uploaded_file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    uploaded_file.save(path)

    language: str = request.form.get("language", "python")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            code: str = fh.read()
        result = invoke_refactor_engine(source=code, language=language, goals=["readability"])
        resp = jsonify(filename=filename, **result)
        resp.status_code = 200
        return resp
    except RuntimeError as e:
        message = str(e)
        if "OPENAI_QUOTA_EXCEEDED" in message or "insufficient_quota" in message:
            status = 429
        elif "OPENAI_API_KEY is required" in message:
            status = 503
        elif "OPENAI_AUTH_ERROR" in message:
            status = 401
        else:
            status = 500
        resp = jsonify(error="refactor failed", detail=message)
        resp.status_code = status
        return resp
    except Exception as e:
        resp = jsonify(error="upload/refactor failed", detail=str(e))
        resp.status_code = 500
        return resp


@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_e: RequestEntityTooLarge) -> Response:
    """
    Translate large upload errors into a clear 413 response.
    """
    resp = jsonify(error="file too large (max 4 MB)")
    resp.status_code = 413
    return resp


if __name__ == "__main__":
    # Bind to 0.0.0.0 so the app works inside containers and on remote hosts
    # The PORT environment variable can change the port for platforms such as Render or Fly
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
