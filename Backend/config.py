# config.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    upload_dir: str
    max_bytes: int
    frontend_origin: str
    openai_model: str

def load_settings() -> Settings:
    base = os.path.dirname(os.path.abspath(__file__))
    return Settings(
        upload_dir=os.path.join(base, "uploads"),
        max_bytes=int(os.getenv("MAX_CONTENT_LENGTH", "4000000")),
        # A frontend origin is the trio of scheme, host, and port
        # Example for local dev: http://localhost:5500
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:5500"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
