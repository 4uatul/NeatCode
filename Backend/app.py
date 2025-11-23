import os
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import google.generativeai as genai
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Environment & configuration
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR.parent / "uploads"

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "5000"))

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to Backend/.env "
                       "as GEMINI_API_KEY=your_api_key_here")

genai.configure(api_key=GEMINI_API_KEY)

# Use any Gemini model you have access to
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
model = genai.GenerativeModel(MODEL_NAME)

# -------------------------------------------------------------------
# Flask app
# -------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # allow requests from localhost:3000

# Ensure uploads directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = { "txt", "js", "py", "java", "cpp", "c", "cs", "php", "html", "css",
                       "json", "xml", "rb", "swift"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------------------------
# Helper: call Gemini to refactor code
# -------------------------------------------------------------------

def refactor_with_gemini(code: str, filename: str | None = None) -> dict:
    """
    Sends the original code to Gemini and asks for the refactored code as well as an
    explanation of what changed. It returns a dict with keys: refactored_code, explanation
    """
    language_hint = ""
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        language_hint = f" (file extension .{ext})"

    prompt = f"""
			You are a senior software engineer helping a student with code refactoring.
			They have provided the following source code{language_hint}. Your job:
			1. Refactor and improve readability, structure, and maintainability.
			2. Fix obvious bugs, but **do not** change the external behavior.
			3. Apply good naming, modularization, and comments where helpful.
			4. Keep the same language as the input.
			
			Return your answer in **pure JSON** with the following keys:
			- "refactored_code": the improved version of the code only.
			- "explanation": a clear bullet-point style explanation of the most important changes.
			
			Here is the original code:
			
			```code
			{code}
			"""


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
	return jsonify({"status": "ok",
	                "timestamp": datetime.utcnow().isoformat() + "Z",
	                "model": MODEL_NAME})
	
@app.route("/api/refactor", methods=["POST"])
def refactor_code():
	"""
	JSON endpoint for code pasted in the UI.
	Expected request JSON:
	{
	  "code": "string with source code",
	  "filename": "some_filename.ext"
	}
	
	Response:
	{
	  "originalCode": "...",
	  "refactoredCode": "...",
	  "explanation": "..."
	}
	"""
	data = request.get_json(silent=True) or {}
	code = data.get("code", "")
	filename = data.get("filename")

	if not code.strip():
		return jsonify({"error": "No code provided"}), 400

	try:
		gemini_result = refactor_with_gemini(code, filename)
		return jsonify({"originalCode": code,
		                "refactoredCode": gemini_result["refactored_code"],
		                "explanation": gemini_result["explanation"],})
	except Exception as e:
		# Log server-side in real app; here we just return a safe error
		return jsonify({"error": "Failed to refactor code with Gemini.",
		                "details": str(e)}), 500
    
@app.route("/api/refactor-file", methods=["POST"])
def refactor_file():
	"""
	Multipart/form-data endpoint for uploaded files.
	Expected form:
	  file: uploaded code file
	
	Response JSON shape matches /api/refactor.
	"""
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
	
	# Optionally save the original file for audit/history
	with open(save_path, "w", encoding="utf-8") as f:
		f.write(file_contents)
	
	if not file_contents.strip():
		return jsonify({"error": "Uploaded file is empty"}), 400
	
	try:
		gemini_result = refactor_with_gemini(file_contents, filename)
		return jsonify({"filename": filename,
		                "originalCode": file_contents,
		                "refactoredCode": gemini_result["refactored_code"],
		                "explanation": gemini_result["explanation"],})
	except Exception as e:
		return jsonify({"error": "Failed to refactor uploaded file with Gemini.",
		                "details": str(e)}), 500


# -------------------------------------------------------------------
# Main entrypoint
# -------------------------------------------------------------------

if name == "main":
# For local dev; in production use gunicorn/uwsgi, etc.
app.run(host="0.0.0.0", port=PORT, debug=True)
