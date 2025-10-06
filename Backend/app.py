import os
from typing import Any
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
from services.ai_client import invoke_refactor_engine  # renamed import

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.update(UPLOAD_FOLDER=UPLOAD_DIR, MAX_CONTENT_LENGTH=4_000_000,)

CORS(app,resources={r"/api/*": {"origins": ["https://4uatul.github.io"]}},
    supports_credentials=False, max_age=600,)

@app.get("/health")
def get_health_status() -> Response:
    resp = jsonify(status="ok")
    resp.status_code = 200
    return resp

@app.post("/api/refactor")
def post_refactor_request() -> Response:
    try:
        data: dict[str, Any] = request.get_json(silent=True) or request.form.to_dict() or {}
    except BadRequest:
        resp = jsonify(error="invalid JSON")
        resp.status_code = 400
        return resp

    source: str = (data.get("source") or "").strip()
    language: str = data.get("language", "python")
    goals: list[str] = data.get("goals") or ["readability", "remove dead code", "style/PEP8"]

    if not source:
        resp = jsonify(error="'source' is required")
        resp.status_code = 400
        return resp

    try:
        result = invoke_refactor_engine(source=source, language=language, goals=goals)
        resp = jsonify(result)
        resp.status_code = 200
        return resp
    except Exception as e:
        resp = jsonify(error="refactor failed", detail=str(e))
        resp.status_code = 500
        return resp

@app.post("/api/upload")
def post_upload_request() -> Response:
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        resp = jsonify(error="missing file")
        resp.status_code = 400
        return resp

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
    except Exception as e:
        resp = jsonify(error="upload/refactor failed", detail=str(e))
        resp.status_code = 500
        return resp

@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_e: RequestEntityTooLarge) -> Response:
    resp = jsonify(error="file too large (max 4 MB)")
    resp.status_code = 413
    return resp

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
