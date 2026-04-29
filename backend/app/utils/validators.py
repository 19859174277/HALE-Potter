import os

REQUIRED_FILES = [
    "GH_Copilot_Knowledge_Base_Final.csv",
    "Tool_1_Radar_Diagnosis.py",
    "Tool_2_Sankey_Optimizer.py",
    "模版.docx",
    "HALE_Potter.PNG",
    "User.PNG",
]

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")

def validate_assets():
    missing = []
    for fname in REQUIRED_FILES:
        fpath = os.path.join(ROOT_DIR, fname)
        if not os.path.exists(fpath):
            missing.append(fname)
    if missing:
        raise RuntimeError(f"Missing required assets in project root: {missing}")
    return True
