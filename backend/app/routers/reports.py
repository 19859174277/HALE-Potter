import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.models.schemas import ReportGenerateRequest
from app.services import report_generator

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate")
async def generate_report(req: ReportGenerateRequest):
    try:
        from app.services import ner_service
        df = ner_service.get_df()
        row = df[df["ISO_Code"] == req.iso_code]
        country_name = str(row.iloc[0]["Country_Name"]) if not row.empty else req.iso_code
        path = report_generator.generate_report(req.session_id, req.iso_code, country_name, req.policy_text)
        return {"download_url": f"/api/reports/download/{req.session_id}"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/download/{session_id}")
async def download_report(session_id: str):
    path = os.path.join(report_generator.OUTPUT_DIR, f"report_{session_id}.docx")
    if not os.path.exists(path):
        return {"error": "Report not found"}
    return FileResponse(path, filename=f"HALE_Potter_Report_{session_id}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
