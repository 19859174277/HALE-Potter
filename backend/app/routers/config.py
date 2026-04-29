import os
import json
from fastapi import APIRouter
from app.models.schemas import ConfigSchema

router = APIRouter(prefix="/api/config", tags=["config"])

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")

def _read():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _write(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get("")
async def get_config():
    cfg = _read()
    # Mask key partially for security
    key = cfg.get("kimi_api_key", "")
    if key and len(key) > 12:
        cfg["kimi_api_key_masked"] = key[:6] + "..." + key[-6:]
    # Never expose the full key in API response
    cfg.pop("kimi_api_key", None)
    return cfg

@router.post("")
async def set_config(cfg: ConfigSchema):
    _write(cfg.model_dump())
    return {"status": "ok"}
