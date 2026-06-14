import json
import random
import string
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent import run_agent

app = FastAPI(title="Claw-a-thon Travel Agent")

SESSIONS_DIR = Path(__file__).parent.parent / "data" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

_sessions: dict[str, dict] = {}


# ── Session helpers ────────────────────────────────────────────────────────────

def _session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def _load_session(session_id: str) -> dict:
    if session_id in _sessions:
        return _sessions[session_id]
    path = _session_path(session_id)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        _sessions[session_id] = data
        return data
    data = {"session_id": session_id, "messages": [], "bookings": []}
    _sessions[session_id] = data
    return data


def _save_session(session_id: str) -> None:
    data = _sessions.get(session_id)
    if not data:
        return
    with open(_session_path(session_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_or_create_session(request: Request, response: Response) -> tuple[str, dict]:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )
    return session_id, _load_session(session_id)


def _make_booking_ref() -> str:
    chars = string.ascii_uppercase + string.digits
    return "CLA-" + "".join(random.choices(chars, k=6))


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class BookRequest(BaseModel):
    sku_id: str
    summary: str
    total_price: float
    currency: str = "VND"
    passenger: dict
    payment_method: str = "ZaloPay"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request, response: Response):
    session_id, session = _get_or_create_session(request, response)

    session["messages"].append({"role": "user", "content": body.message})

    try:
        text, structured = run_agent(session["messages"])
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"text": f"Lỗi hệ thống: {str(e)}", "structured": None},
        )

    assistant_content = text
    if structured:
        import json as _json
        assistant_content = text + "\n```json\n" + _json.dumps(structured, ensure_ascii=False) + "\n```"

    session["messages"].append({"role": "assistant", "content": assistant_content})
    _save_session(session_id)

    return {"text": text, "structured": structured}


@app.post("/api/book")
async def book(body: BookRequest, request: Request, response: Response):
    session_id, session = _get_or_create_session(request, response)

    ref = _make_booking_ref()
    booking = {
        "booking_ref": ref,
        "sku_id": body.sku_id,
        "summary": body.summary,
        "total_price": body.total_price,
        "currency": body.currency,
        "passenger": body.passenger,
        "payment_method": body.payment_method,
        "booked_at": datetime.utcnow().isoformat(),
    }
    session["bookings"].append(booking)
    _save_session(session_id)

    return {
        "booking_ref": ref,
        "summary": body.summary,
        "total_price": body.total_price,
        "currency": body.currency,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/history")
async def history(request: Request, response: Response):
    session_id, session = _get_or_create_session(request, response)
    return {"bookings": session.get("bookings", [])}


# ── Static files (must be last) ───────────────────────────────────────────────

app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
