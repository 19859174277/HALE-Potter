import os
import json
from typing import List, Dict, Any, AsyncIterator
from anthropic import AsyncAnthropic

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")

def _load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_client():
    cfg = _load_config()
    api_key = cfg.get("kimi_api_key", "")
    base_url = cfg.get("kimi_base_url", "https://api.kimi.com/coding/")
    return AsyncAnthropic(api_key=api_key, base_url=base_url)

SYSTEM_PROMPT_TOOL = """你是一位精通公共卫生经济学与健康计量学的政策分析专家，擅长将量化证据转化为可执行的健康系统优化建议。

用户请求分析某个国家的健康系统。以下是由 HALE-Potter 决策引擎生成的两份核心诊断报告：

【多维基准画像诊断】
{radar_report}

【资源重组Pareto最优决策引擎输出】
{sankey_report}

请基于上述严格的量化结果，撰写一份结构化、可直接落地的中文政策分析报告，要求：
1. 使用 Markdown 格式，标题层级清晰；
2. 涉及数学模型（如 MO-QPO、DEA、CATE）时用 LaTeX 公式表示；
3. 语言风格专业、严谨、凝练，聚焦策略本身，拒绝空话套话；
4. 包含：执行摘要、现状诊断、优化路径、实施建议、风险提示五个部分。
5. 【绝对禁止】严禁在输出中出现任何形式的公文落款、报告编号、发布机构名称、密级标注（如“公开级”）或生成日期。输出内容必须是纯粹的分析与策略建议，不得包含任何格式化抬头或结尾署名。
6. 【表格格式规范】若需使用表格呈现数据，必须采用标准 Markdown 表格语法（| 列1 | 列2 |），表头行与分隔行（|:---|）之间严禁留空行，表格前后需与正文段落以空行隔开。禁止使用 HTML 表格标签。
7. 【公式格式规范】行间公式（$$...$$）结束后必须留一个空行，再继续后续正文或表格。行内公式（$...$）不得跨行。LaTeX 公式内部如需换行，请使用 aligned 环境并保证 $$ 成对出现。
8. 【重要】请在报告中合适的位置插入诊断图表占位符：
   - 在【现状诊断】或基准画像分析段落之后，插入 Markdown 图片：![{country_name} 健康系统6维雷达诊断](RADAR_PLACEHOLDER)
   - 在【优化路径】或资源重组分析段落之后，插入 Markdown 图片：![{country_name} 资源重组桑基流向](SANKEY_PLACEHOLDER)
   这样用户可以在阅读文字时同步看到对应的量化图表。
"""

SYSTEM_PROMPT_CHAT = """你是一位全球卫生政策智库助手 HALE-Potter，精通公共卫生经济学、健康计量学与卫生体系研究。
请用专业、严谨但易懂的方式回答用户问题。涉及数学公式请使用 LaTeX 格式。"""

async def stream_tool_response(
    messages: List[Dict[str, str]],
    radar_report: str,
    sankey_report: str,
    country_name: str = "",
) -> AsyncIterator[str]:
    client = get_client()
    system = SYSTEM_PROMPT_TOOL.format(
        radar_report=radar_report,
        sankey_report=sankey_report,
        country_name=country_name,
    )
    async with client.messages.stream(
        model="kimi-k2.5",
        max_tokens=4096,
        system=system,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text

async def stream_chat_response(
    messages: List[Dict[str, str]],
) -> AsyncIterator[str]:
    client = get_client()
    async with client.messages.stream(
        model="kimi-k2.5",
        max_tokens=4096,
        system=SYSTEM_PROMPT_CHAT,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
