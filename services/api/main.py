"""Minimal P-IA-NO API; no musical processing at checkpoint 0.2."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="P-IA-NO", version="0.0.2", docs_url=None, redoc_url=None)
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "p-ia-no-api", "version": "0.0.2",
            "capabilities": {"uploads": False, "training": False, "arrangement": False}}
# Local production preview: web and API share an origin. API routes take precedence.
web_dist = Path(__file__).resolve().parents[2] / "apps/web/dist"
if web_dist.is_dir():
    app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")
