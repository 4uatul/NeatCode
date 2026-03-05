import code
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR.parent / "uploads"
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "5000"))
HOST = "0.0.0.0"

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to Backend/.env")

genai.configure(api_key=GEMINI_API_KEY)

# Free-tier model cascade: best quality → fastest/highest quota
MODEL_CHAIN = [
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),        # primary  — best quality
    "gemini-2.5-flash-lite",                              # fallback 1
    "gemini-3-flash-preview",                             # fallback 2
    "gemini-3.1-flash-lite-preview",                      # fallback 3
    "gemini-2.0-flash",                                   # fallback 4
    "gemini-2.0-flash-lite",                              # fallback 5 — highest RPD
]
_model_instances = {m: genai.GenerativeModel(m) for m in MODEL_CHAIN}

# Flask app setup
app = Flask(__name__)
CORS(app)

# Ensure uploads directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"txt", "js", "py", "java", "cpp", "c", "cs", "php", "html", "css", "json", "xml", "rb", "swift"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def refactor_with_gemini(code: str, filename: Optional[str] = None) -> dict:
    language_hint = ""
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        language_hint = f" (file extension .{ext})"

    prompt = f"""You are NeatCode, a strict code refactoring tool. Your ONLY job is to refactor code.

GUARD RAILS — check this first:
- If the input is NOT source code (e.g. it's a question, essay, chat message, or random text), do NOT refactor it.
  Instead return JSON with "not_code": true and a helpful "message" field explaining that NeatCode only refactors code,
  and suggest what the user should do (e.g. paste actual code, upload a file, try the sample).
  Example: {{"not_code": true, "message": "It looks like you pasted plain text instead of code. NeatCode only refactors source code. Try pasting a Python, JavaScript, or other code snippet, or click \\"Try Sample\\" to see an example."}}

If the input IS code, refactor it following these RULES exactly:
- Fix naming: use clear, descriptive names (snake_case for Python, camelCase for JS/Java)
- Fix formatting and indentation
- Simplify logic where obviously redundant (e.g. nested ifs that can be flattened)
- Use idiomatic built-ins where appropriate (e.g. sum(), any(), all())
- Add minimal inline comments only where the logic is non-obvious — one short comment per logical block, never restate what the code already says clearly
- Do NOT add extra error handling, validation, or features that weren't in the original
- Do NOT add type hints unless the original had them
- Keep the refactored code concise — shorter or same length, never longer
- Preserve the exact same functionality and output as the original

Code to refactor:
```
{code}
```

Respond with ONLY a valid JSON object — no markdown, no code fences, no extra text.

If it IS code:
{{
  "project_summary": "One sentence describing what the code does.",
  "refactored_code": "the refactored code as a plain string with \\n for newlines",
  "key_changes": [
    {{"change": "short label", "reason": "one sentence why"}}
  ]
}}

If it is NOT code:
{{"not_code": true, "message": "helpful message here"}}"""

    # Try each model in the chain, falling back on quota/rate-limit errors
    last_error = None
    response = None
    for model_name in MODEL_CHAIN:
        try:
            response = _model_instances[model_name].generate_content(prompt)
            print(f"Used model: {model_name}")
            break
        except Exception as e:
            if any(code in str(e) for code in ("429", "quota", "RESOURCE_EXHAUSTED")):
                print(f"{model_name} quota hit, trying next model...")
                last_error = e
            else:
                raise
    if response is None:
        raise last_error
    response_text = response.text.strip()

    # Debug: Print what Gemini actually returned
    print("=" * 50)
    print("RAW GEMINI RESPONSE:")
    print(response_text)
    print("=" * 50)

    # Remove markdown code blocks if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Debug: Print cleaned response
    print("CLEANED RESPONSE:")
    print(response_text)
    print("=" * 50)

    result = json.loads(response_text)
    # ----------------------------
    return result

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "NeatCode Backend API",
        "status": "running",
        "endpoints": ["/api/health", "/api/refactor", "/api/refactor-file"]
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models": MODEL_CHAIN
    })

@app.route("/api/refactor", methods=["POST"])
def refactor_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    filename = data.get("filename")

    if not code.strip():
        return jsonify({"error": "No code provided"}), 400

    try:
        gemini_result = refactor_with_gemini(code, filename)

        if gemini_result.get("not_code"):
            return jsonify({"notCode": True, "message": gemini_result["message"]}), 422

        return jsonify({
            "originalCode": code,
            "refactoredCode": gemini_result["refactored_code"],
            "projectSummary": gemini_result["project_summary"],
            "keyChanges": gemini_result["key_changes"]
        })
    except Exception as e:
        import traceback
        print("ERROR in refactor_code:")
        print(traceback.format_exc())
        return jsonify({
            "error": "Failed to refactor code with Gemini.",
            "details": str(e)
        }), 500

@app.route("/api/refactor-file", methods=["POST"])
def refactor_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    save_path = UPLOAD_DIR / filename
    file_contents = file.read().decode("utf-8", errors="replace")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(file_contents)

    if not file_contents.strip():
        return jsonify({"error": "Uploaded file is empty"}), 400

    try:
        gemini_result = refactor_with_gemini(file_contents, filename)
        return jsonify({
            "original_code": code,
            "refactored_code": gemini_result["refactored_code"],
            "project_summary": gemini_result["project_summary"],
            "key_changes": gemini_result["key_changes"]
        })
    except Exception as e:
        return jsonify({
            "error": "Failed to refactor uploaded file with Gemini.",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
