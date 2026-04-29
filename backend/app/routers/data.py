import pandas as pd
import os
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/data", tags=["data"])

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
CSV_PATH = os.path.join(ROOT_DIR, "GH_Copilot_Knowledge_Base_Final.csv")

@router.get("/countries")
async def get_countries(
    sort_by: str = Query("HALE_Percentile", description="Column to sort by"),
    order: str = Query("desc", description="asc or desc"),
    limit: int = Query(50, ge=1, le=500),
    search: str = Query("", description="Filter by country name or ISO"),
):
    df = pd.read_csv(CSV_PATH)
    if search:
        mask = (
            df["ISO_Code"].astype(str).str.contains(search, case=False, na=False)
            | df["Country_Name"].astype(str).str.contains(search, case=False, na=False)
        )
        df = df[mask]
    if sort_by in df.columns:
        ascending = order.lower() == "asc"
        df = df.sort_values(by=sort_by, ascending=ascending)
    df = df.head(limit)
    return {
        "total": len(df),
        "countries": df.fillna("").to_dict(orient="records"),
    }
