import code
import os
import json
from datetime import datetime
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
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
model = genai.GenerativeModel(MODEL_NAME)

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

    prompt = f"""You are a code refactoring assistant. Analyze and refactor the following {language_hint} code.

IMPORTANT: You MUST respond with ONLY a valid JSON object. Do not include any markdown, code blocks, or explanatory text outside the JSON.

Code to refactor:
```
{code}
```

You MUST return a JSON object with exactly these three fields:

1. "project_summary" - A brief 2-3 sentence description of what this code does
2. "refactored_code" - The improved version of the code
3. "key_changes" - An array of objects, each with "change" and "reason" fields

Example response format:
{{
  "project_summary": "This code calculates the total price of items in a shopping cart with discount logic.",
  "refactored_code": "function calculateTotal(items) {{\\n  return items.reduce((sum, item) => sum + item.price, 0);\\n}}",
  "key_changes": [
    {{"change": "Renamed variable 'x' to 'items'", "reason": "Descriptive names improve code readability"}},
    {{"change": "Used reduce instead of for loop", "reason": "More functional and concise approach"}}
  ]
}}

Now refactor the code above and return your response as JSON only."""

    response = model.generate_content(prompt)
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
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": MODEL_NAME
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
