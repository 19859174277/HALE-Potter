from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id: str
    message: str
    alpha: float = Field(default=0.5517, ge=0.0, le=1.0)
    beta: float = Field(default=0.0125, ge=0.0, le=1.0)

class ToolRunRequest(BaseModel):
    alpha: float = Field(default=0.5517, ge=0.0, le=1.0)
    beta: float = Field(default=0.0125, ge=0.0, le=1.0)

class ToolRunResponse(BaseModel):
    iso: str
    radar_image: Optional[str] = None
    sankey_image: Optional[str] = None
    radar_report: Optional[str] = None
    sankey_report: Optional[str] = None
    error: Optional[str] = None

class ReportGenerateRequest(BaseModel):
    session_id: str
    iso_code: str
    policy_text: str

class ConfigSchema(BaseModel):
    kimi_api_key: str
    kimi_base_url: str = "https://api.kimi.com/coding/"
    alpha: float = 0.5517
    beta: float = 0.0125
