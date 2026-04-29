import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "模版.docx")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated_reports")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated_images")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_report(session_id: str, iso_code: str, country_name: str, policy_text: str) -> str:
    doc = DocxTemplate(TEMPLATE_PATH)

    radar_img_name = f"Radar_{iso_code}_{session_id}.png"
    sankey_img_name = f"Sankey_{iso_code}_{session_id}.png"
    radar_path = os.path.join(IMAGE_DIR, radar_img_name)
    sankey_path = os.path.join(IMAGE_DIR, sankey_img_name)

    context = {
        "country_name": country_name,
        "iso_code": iso_code,
        "policy_text": policy_text,
    }

    if os.path.exists(radar_path):
        context["radar_image"] = InlineImage(doc, radar_path, width=Mm(140))
    else:
        context["radar_image"] = "[雷达图未生成]"

    if os.path.exists(sankey_path):
        context["sankey_image"] = InlineImage(doc, sankey_path, width=Mm(160))
    else:
        context["sankey_image"] = "[桑基图未生成]"

    doc.render(context)

    out_path = os.path.join(OUTPUT_DIR, f"report_{session_id}.docx")
    doc.save(out_path)
    return out_path
