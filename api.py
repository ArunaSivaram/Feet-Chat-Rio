"""FastAPI wrapper over the NovaCell RAG chain.

Exposes:
  POST /api/chat     -> Server-Sent Events: token deltas, then a final `docs`
                       event with retrieved sources.
  POST /api/feedback -> Appends a row to feedback_log.csv.
  GET  /api/samples  -> Returns the sample questions shown in the sidebar.
  GET  /api/health   -> Liveness.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from typing import AsyncIterator, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from chain import stream_answer
from config import FEEDBACK_LOG

SAMPLE_QUESTIONS = [
    "Why is my mobile internet so slow?",
    "How do I activate international roaming?",
    "My new SIM still shows No Service — what should I do?",
    "What are the roaming charges in the EU?",
    "How do I enable Wi-Fi calling?",
    "How do I set up AutoPay?",
]


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class FeedbackRequest(BaseModel):
    message_id: str
    question: str
    answer: str
    rating: Literal["up", "down"]


app = FastAPI(title="NovaCell Support API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _stream_chat(question: str) -> AsyncIterator[str]:
    try:
        token_iter, docs = stream_answer(question)
    except RuntimeError as exc:
        yield _sse("error", {"message": str(exc)})
        return

    for token in token_iter:
        if token:
            yield _sse("token", {"text": token})

    docs_payload = [
        {
            "source": str(d.metadata.get("source", "?")),
            "source_id": str(d.metadata.get("source_id", "?")),
            "relevance_score": d.metadata.get("relevance_score"),
            "content": d.page_content,
        }
        for d in docs
    ]
    yield _sse("docs", {"docs": docs_payload})
    yield _sse("done", {})


@app.post("/api/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _stream_chat(req.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/feedback")
async def feedback(req: FeedbackRequest) -> dict:
    is_new = not FEEDBACK_LOG.exists()
    with FEEDBACK_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(
                ["timestamp", "message_id", "rating", "question", "answer"]
            )
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                req.message_id,
                req.rating,
                req.question,
                req.answer,
            ]
        )
    return {"ok": True}


@app.get("/api/samples")
async def samples() -> dict:
    return {"questions": SAMPLE_QUESTIONS}


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
