# gunicorn.conf.py
import os

# Let platforms like Render/Fly set PORT; default to 8080 locally
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"

# Tuneables (safe defaults). You can override via env vars.
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
