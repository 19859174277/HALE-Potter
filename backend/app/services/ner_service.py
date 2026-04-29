import pandas as pd
import os
import re
from typing import Optional, Tuple

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
CSV_PATH = os.path.join(ROOT_DIR, "GH_Copilot_Knowledge_Base_Final.csv")

# Common aliases for robust matching
ALIASES = {
    "中国": "CHN",
    "中华人民共和国": "CHN",
    "美国": "USA",
    "美利坚": "USA",
    "美利坚合众国": "USA",
    "日本": "JPN",
    "印度": "IND",
    "英国": "GBR",
    "德国": "DEU",
    "法国": "FRA",
    "巴西": "BRA",
    "俄罗斯": "RUS",
    "俄罗斯联邦": "RUS",
}

def load_country_map():
    df = pd.read_csv(CSV_PATH, usecols=["ISO_Code", "Country_Name"])
    return df

def detect_country(text: str) -> Optional[Tuple[str, str]]:
    """Return (iso_code, country_name) if detected, else None.
    NOTE: Reloads CSV on every call to reflect file updates without restart.
    """
    if not text:
        return None

    df = load_country_map()
    text_upper = text.upper().strip()

    # 1. Exact ISO match (word boundary)
    for _, row in df.iterrows():
        iso = str(row["ISO_Code"]).strip().upper()
        if iso in text_upper.split() or re.search(rf"\b{re.escape(iso)}\b", text_upper):
            return iso, str(row["Country_Name"]).strip()

    # 2. Country name substring match (中文 or English)
    best_match = None
    best_len = 0
    for _, row in df.iterrows():
        name = str(row["Country_Name"]).strip()
        if not name:
            continue
        if name.upper() in text_upper and len(name) > best_len:
            best_len = len(name)
            best_match = (str(row["ISO_Code"]).strip().upper(), name)

    if best_match:
        return best_match

    # 3. Alias fallback
    for alias, iso in ALIASES.items():
        if alias.upper() in text_upper:
            row = df[df["ISO_Code"] == iso]
            if not row.empty:
                return iso, str(row.iloc[0]["Country_Name"]).strip()

    return None
