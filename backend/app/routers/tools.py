from fastapi import APIRouter
from app.models.schemas import ToolRunResponse, ToolRunRequest
from app.services import tool_runner

router = APIRouter(prefix="/api/tools", tags=["tools"])

@router.post("/run/{iso_code}", response_model=ToolRunResponse)
async def run_tools(iso_code: str, req: ToolRunRequest):
    import uuid
    session_id = str(uuid.uuid4())
    radar_img, sankey_img, radar_report, sankey_report = await tool_runner.run_tools(
        iso_code, session_id, alpha=req.alpha, beta=req.beta
    )
    if radar_img is None:
        return ToolRunResponse(iso=iso_code, error=radar_report or "Unknown error")
    return ToolRunResponse(
        iso=iso_code,
        radar_image=radar_img,
        sankey_image=sankey_img,
        radar_report=radar_report,
        sankey_report=sankey_report,
    )
