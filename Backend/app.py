# app.py
import os, json, re
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# ------------- Load .env -------------

# This lets you keep GEMINI_API_KEY and FRONTEND_ORIGIN in a .env file
# in the same folder as app.py.
load_dotenv()

# ------------- Configure -------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Mock when there is no key OR when using a demo/placeholder key
MOCK_MODE = False
if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("sk-demo-not-"):
    MOCK_MODE = True
    print("MOCK_MODE =", MOCK_MODE)
else:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="NeatCode Backend", version="1.0.0")

# In CORS, the FRONTEND_ORIGIN refers to where the page is hosted, defined by
# its scheme, host, and port (without the path). For example, http://localhost:5500
# and http://127.0.0.1:5500 count as two distinct origins even though they reach
# the same machine. In local development, backends often allow both origins so
# requests succeed whether the page is loaded via localhost or 127.0.0.1 on
# the same port.
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")

ALLOWED_ORIGINS = [
    FRONTEND_ORIGIN,
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------- Models -------------
class RefactorRequest(BaseModel):
    code: str
    language: Optional[str] = "auto"


class RefactorResponse(BaseModel):
    refactored_code: str
    explanation: str


# ------------- Routes -------------
@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/refactor", response_model=RefactorResponse)
def refactor(req: RefactorRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Empty code.")
    return _call_gemini(req.code, req.language or "auto")


# ------------- Provider call -------------
def _call_gemini(code: str, language: str) -> RefactorResponse:
    if MOCK_MODE:
        language_name = language or "auto"
        return RefactorResponse(
            refactored_code=(
                f"// Mock refactor ({language_name})\n"
                "// Backend is running in mock mode (no GEMINI_API_KEY)\n\n"
                f"{code}\n\n"
                "// End of mock refactor"
            ),
            explanation=(
                "Gemini API key is not configured. "
                "This is a mock response from the backend."
            ),
        )

    model = genai.GenerativeModel(MODEL_NAME)

    schema = {
        "type": "object",
        "properties": {
            "refactored_code": {"type": "string"},
            "explanation": {"type": "string"},
        },
        "required": ["refactored_code", "explanation"],
        "additionalProperties": False,
    }

    prompt = f"""
You are a senior software engineer. Refactor the user's code without changing behavior.

Language: {language}
Keep public interfaces stable. Prefer idiomatic patterns. Remove duplication, improve naming,
and add light comments only where helpful. If the code is already clean, keep it mostly unchanged and explain why.

Return ONLY JSON compatible with this schema:
{json.dumps(schema, indent=2)}

User code: <code>
{code}
</code>
"""

    cfg = genai.GenerationConfig(
        temperature=0.2,
        top_p=0.9,
        candidate_count=1,
        max_output_tokens=4096,
        # Newer SDKs may honor this and return raw JSON (no fences). Harmless if ignored.
        response_mime_type="application/json",
    )

    resp = model.generate_content(prompt, generation_config=cfg)
    text = (resp.text or "").strip()
    # Strip accidental ```json fences if the model adds them
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)

    try:
        data = json.loads(text)
        return RefactorResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Provider returned unexpected format: {e}. Snippet: {text[:400]}",
        )