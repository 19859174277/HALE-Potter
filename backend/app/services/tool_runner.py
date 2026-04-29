import os
import asyncio
import importlib.util
from typing import Optional, Tuple

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
TOOL1_PATH = os.path.join(ROOT_DIR, "Tool_1_Radar_Diagnosis.py")
TOOL2_PATH = os.path.join(ROOT_DIR, "Tool_2_Sankey_Optimizer.py")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated_images")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load modules dynamically to avoid path issues
def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_tool1 = _load_module("tool1", TOOL1_PATH)
_tool2 = _load_module("tool2", TOOL2_PATH)

async def run_tools(
    iso_code: str,
    session_id: str,
    alpha: float = 0.5517,
    beta: float = 0.0125,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Returns (radar_image_name, sankey_image_name, radar_report, sankey_report)
    """
    db_path = os.path.join(ROOT_DIR, "GH_Copilot_Knowledge_Base_Final.csv")

    # Ensure matplotlib saves images to ROOT_DIR (where the tool scripts expect)
    original_cwd = os.getcwd()
    os.chdir(ROOT_DIR)

    try:
        # Run Tool_1 in threadpool
        radar_report = await asyncio.to_thread(
            _tool1.generate_radar_diagnosis,
            iso_code,
            db_path,
        )
        if radar_report.startswith("Error"):
            return None, None, radar_report, None

        # Run Tool_2 in threadpool
        sankey_report = await asyncio.to_thread(
            _tool2.run_optimization_and_sankey,
            iso_code,
            alpha,
            beta,
            db_path,
        )
        if sankey_report.startswith("Error"):
            return None, None, radar_report, sankey_report

        # Rename outputs to include session_id to avoid collisions
        old_radar = os.path.join(ROOT_DIR, f"Radar_{iso_code}.png")
        old_sankey = os.path.join(ROOT_DIR, f"Sankey_{iso_code}.png")

        new_radar = f"Radar_{iso_code}_{session_id}.png"
        new_sankey = f"Sankey_{iso_code}_{session_id}.png"

        new_radar_path = os.path.join(OUTPUT_DIR, new_radar)
        new_sankey_path = os.path.join(OUTPUT_DIR, new_sankey)

        if os.path.exists(old_radar):
            os.replace(old_radar, new_radar_path)
        if os.path.exists(old_sankey):
            os.replace(old_sankey, new_sankey_path)

        return new_radar, new_sankey, radar_report, sankey_report
    finally:
        os.chdir(original_cwd)
