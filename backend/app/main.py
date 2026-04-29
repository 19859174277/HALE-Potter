import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.utils import validators
from app.models import database as db
from app.routers import chat, tools, reports, data, config

# Cleanup stale images periodically
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_images")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_reports")

async def _cleanup_loop():
    """Remove files older than 24h every 30 minutes."""
    import time
    while True:
        await asyncio.sleep(1800)
        now = time.time()
        for folder in (IMAGE_DIR, REPORT_DIR):
            if not os.path.exists(folder):
                continue
            for fname in os.listdir(folder):
                fpath = os.path.join(folder, fname)
                try:
                    if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > 86400:
                        os.remove(fpath)
                except Exception:
                    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    validators.validate_assets()
    db.init_db()
    # Start background cleanup
    cleanup_task = asyncio.create_task(_cleanup_loop())
    yield
    cleanup_task.cancel()

app = FastAPI(title="HALE-Potter API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images
os.makedirs(IMAGE_DIR, exist_ok=True)
app.mount("/api/static/images", StaticFiles(directory=IMAGE_DIR), name="images")

app.include_router(chat.router)
app.include_router(tools.router)
app.include_router(reports.router)
app.include_router(data.router)
app.include_router(config.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "HALE-Potter"}
