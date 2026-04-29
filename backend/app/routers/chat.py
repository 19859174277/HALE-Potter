import json
import uuid
from typing import AsyncIterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.models import database as db
from app.services import ner_service, tool_runner, kimi_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def _chat_stream(req: ChatRequest) -> AsyncIterator[str]:
    session_id = req.session_id or str(uuid.uuid4())
    db.create_session(session_id)
    db.add_message(session_id, "user", req.message)

    try:
        # --- NER ---
        yield _sse("status", {"step": "NER", "text": "正在检索全球190国健康底座数据库..."})
        country = ner_service.detect_country(req.message)

        if country is None:
            # Casual chat path
            yield _sse("status", {"step": "CHAT", "text": "未检测到国家实体，进入智库自由问答模式..."})
            history = db.get_messages(session_id)
            messages = [{"role": m["role"], "content": m["content"]} for m in history if m["role"] in ("user", "assistant")]

            full_reply = ""
            async for chunk in kimi_service.stream_chat_response(messages):
                full_reply += chunk
                yield _sse("delta", {"content": chunk})

            db.add_message(session_id, "assistant", full_reply)
            yield _sse("done", {})
            return

        iso_code, country_name = country

        # Update session title if it's still default
        sessions = db.get_sessions()
        for s in sessions:
            if s["session_id"] == session_id and (s["title"] == "New Chat" or not s["title"]):
                db.update_session_title(session_id, f"{country_name} ({iso_code})")
                break

        # --- TOOLS: RADAR ---
        yield _sse("status", {"step": "RADAR", "text": f"正在执行 {country_name} 的6维雷达基准画像诊断 (Radar Diagnosis)..."})

        radar_img, sankey_img, radar_report, sankey_report = await tool_runner.run_tools(
            iso_code, session_id, alpha=req.alpha, beta=req.beta
        )

        if radar_img is None:
            err = radar_report or f"该国数据 ({iso_code}) 暂未纳入 190 国底座"
            yield _sse("error", {"message": err})
            return

        yield _sse("image", {"type": "radar", "url": f"/api/static/images/{radar_img}"})

        # --- TOOLS: SANKEY ---
        yield _sse("status", {"step": "SANKEY", "text": f"正在执行 $MO$-$QPO$ 线性规划寻优，注入因果弹性 (CATE)，生成 Pareto 资源重组流向..."})

        if sankey_img is None:
            err = sankey_report or f"该国数据 ({iso_code}) 暂未纳入 190 国底座"
            yield _sse("error", {"message": err})
            return

        yield _sse("image", {"type": "sankey", "url": f"/api/static/images/{sankey_img}"})

        # --- POLICY TEXT via Kimi ---
        yield _sse("status", {"step": "POLICY", "text": "正在调用 Kimi 政策智库模型撰写高规格决策建议..."})

        history = db.get_messages(session_id)
        messages = [{"role": m["role"], "content": m["content"]} for m in history if m["role"] in ("user", "assistant")]

        # Enrich the last user message with tool results
        tool_context = f"\n\n[系统诊断数据 - {country_name} ({iso_code})]\n{radar_report}\n\n{sankey_report}\n"
        if messages and messages[-1]["role"] == "user":
            messages[-1]["content"] = messages[-1]["content"] + tool_context
        else:
            messages.append({"role": "user", "content": req.message + tool_context})

        full_policy = ""
        async for chunk in kimi_service.stream_tool_response(messages, radar_report, sankey_report, country_name):
            full_policy += chunk
            yield _sse("delta", {"content": chunk})

        # Persist assistant message (images stored for reference)
        image_urls = []
        if radar_img:
            image_urls.append(f"/api/static/images/{radar_img}")
        if sankey_img:
            image_urls.append(f"/api/static/images/{sankey_img}")
        db.add_message(session_id, "assistant", full_policy, images=image_urls)
        yield _sse("done", {})

    except Exception as e:
        yield _sse("error", {"message": f"服务内部错误: {str(e)}"})

@router.post("/stream")
async def chat_stream(req: ChatRequest):
    return StreamingResponse(
        _chat_stream(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"session_id": session_id, "messages": db.get_messages(session_id)}

@router.get("/sessions")
async def get_sessions():
    return {"sessions": db.get_sessions()}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    db.delete_session(session_id)
    return {"success": True}
