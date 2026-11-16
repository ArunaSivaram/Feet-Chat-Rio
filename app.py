"""Streamlit UI for the NovaCell support assistant."""
from __future__ import annotations

import csv
import html
import uuid
from datetime import datetime, timezone

import streamlit as st

from chain import stream_answer
from config import FEEDBACK_LOG

SAMPLE_QUESTIONS = [
    "Why is my mobile internet so slow?",
    "How do I activate international roaming?",
    "My new SIM still shows No Service after an hour — what should I do?",
    "What are the roaming charges in the EU?",
    "How do I enable Wi-Fi calling?",
    "How do I set up AutoPay?",
    "My calls keep dropping — what should I check?",
]

SIGNAL_LOGO_SVG = """
<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#0E7C86" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M5 13 Q 9 9 13 13"/>
  <path d="M3 17 Q 9 11 15 17" opacity="0.6"/>
  <path d="M1 21 Q 9 13 17 21" opacity="0.3"/>
  <circle cx="19" cy="18" r="2" fill="#0E7C86" stroke="none"/>
</svg>
"""

st.set_page_config(page_title="NovaCell Support", page_icon="📡", layout="wide")

_CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="st-"], .stMarkdown, .stMarkdown p, .stChatMessage,
.stButton button, .stTextInput input, .stTextArea textarea, .stChatInput textarea {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #1E293B;
    letter-spacing: -0.005em;
}
.stMarkdown p, .stChatMessage p {
    font-size: 15px;
    line-height: 1.6;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter Tight', 'Inter', sans-serif !important;
    color: #1E293B;
    letter-spacing: -0.015em;
}
h1 {
    font-size: 2.25rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.25rem !important;
}
[data-testid="stCaptionContainer"], .stCaption {
    color: #64748B !important;
}

.stApp { background-color: #F7F8FA; }

/* Hide default Streamlit chrome */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer { display: none !important; }

/* Centered 820px chat column */
.main .block-container {
    max-width: 820px !important;
    padding-top: 2rem !important;
    padding-bottom: 7rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* --- Sidebar --- */
section[data-testid="stSidebar"] {
    background-color: #EEF2F6;
    border-right: 1px solid #E2E8F0;
}
.sidebar-brand {
    display: flex; align-items: center; gap: 10px;
    margin: 0 0 0.25rem 0;
}
.sidebar-brand .brand-title {
    font-family: 'Inter Tight', 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: #1E293B;
}
.sidebar-section {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    margin: 1.25rem 0 0.5rem 0;
}
section[data-testid="stSidebar"] .stButton button {
    background: #FFFFFF;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    text-align: left;
    font-weight: 400;
    font-size: 14px;
    padding: 0.5rem 0.75rem 0.5rem 2rem;
    width: 100%;
    position: relative;
    transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease;
}
section[data-testid="stSidebar"] .stButton button::before {
    content: "";
    position: absolute;
    left: 0.75rem; top: 50%;
    width: 14px; height: 14px;
    transform: translateY(-50%);
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'/></svg>");
    background-repeat: no-repeat; background-size: contain;
    opacity: 0.85;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #E6F4F5;
    border-color: #0E7C86;
    color: #0E7C86;
}
section[data-testid="stSidebar"] .stButton button:hover::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230E7C86' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'/></svg>");
}

/* Ghost "Clear conversation" button (tertiary type) */
section[data-testid="stSidebar"] .stButton button[kind="tertiary"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #64748B !important;
    font-size: 13px !important;
    padding: 0.4rem 0.6rem !important;
}
section[data-testid="stSidebar"] .stButton button[kind="tertiary"]::before {
    display: none;
}
section[data-testid="stSidebar"] .stButton button[kind="tertiary"]:hover {
    background: #FEE2E2 !important;
    color: #DC2626 !important;
    border-color: transparent !important;
}

/* --- User message (raw HTML, right-aligned teal bubble) --- */
.user-msg {
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    gap: 10px;
    margin: 20px 0;
    animation: fadeIn 180ms ease-out;
}
.user-bubble {
    background: #0E7C86;
    color: #FFFFFF;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    max-width: 70%;
    font-size: 15px;
    line-height: 1.55;
    word-wrap: break-word;
}
.chat-avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
}
.user-avatar {
    background: #E6F4F5;
    color: #0E7C86;
}

/* --- Assistant message (st.chat_message styled as white card) --- */
[data-testid="stChatMessage"] {
    background: #FFFFFF !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin: 20px 0 !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06);
    animation: fadeIn 180ms ease-out;
}
/* Teal avatar for assistant */
[data-testid="stChatMessage"] [data-testid*="chatAvatar"],
[data-testid="stChatMessage"] [data-testid*="hatMessageAvatar"],
[data-testid="stChatMessage"] img[alt*="avatar"] {
    background-color: #0E7C86 !important;
    border-radius: 50% !important;
}
/* Numbered lists: teal markers */
[data-testid="stChatMessage"] ol > li::marker {
    color: #0E7C86;
    font-weight: 600;
}

/* --- Chat input (fixed to bottom, white card) --- */
[data-testid="stChatInput"] {
    background: transparent !important;
}
[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #0E7C86 !important;
    box-shadow: 0 0 0 3px rgba(14,124,134,0.15) !important;
}
[data-testid="stChatInput"] textarea {
    color: #1E293B !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
}
[data-testid="stChatInput"] button {
    background: #0E7C86 !important;
    color: #FFFFFF !important;
    border-radius: 999px !important;
    width: 36px !important; height: 36px !important;
    transition: background-color 150ms ease;
}
[data-testid="stChatInput"] button:hover:not(:disabled) {
    background: #13A3AE !important;
}
[data-testid="stChatInput"] button:disabled {
    background: #CBD5E1 !important;
    opacity: 1 !important;
    cursor: not-allowed !important;
}

/* --- Sources expander --- */
[data-testid="stExpander"] {
    background: #F1F5F9 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    margin-top: 12px;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    color: #1E293B !important;
    font-size: 14px !important;
}
[data-testid="stExpander"] summary:hover {
    color: #0E7C86 !important;
}

/* --- Source cards (details/summary pattern) --- */
.source-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    transition: border-color 150ms ease;
}
.source-card:hover {
    border-color: #CBD5E1;
}
.source-card > summary {
    list-style: none;
    cursor: pointer;
    display: block;
}
.source-card > summary::-webkit-details-marker { display: none; }
.source-head {
    display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
}
.source-tag {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 999px;
    text-transform: uppercase;
}
.source-tag.faq { background: #E2E8F0; color: #334155; }
.source-tag.ticket { background: #FEF3C7; color: #B45309; }
.source-tag.guide { background: #E6F4F5; color: #0E7C86; }
.source-id {
    font-size: 12px; color: #64748B; font-weight: 500; font-family: 'Inter', monospace;
}
.source-body {
    font-size: 14px;
    color: #334155;
    line-height: 1.55;
    margin-top: 2px;
}
.source-card:not([open]) .source-body {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.source-toggle {
    display: inline-block;
    margin-top: 6px;
    font-size: 13px;
    color: #0E7C86;
    font-weight: 500;
}
.source-card:not([open]) .source-toggle::after { content: "Show more ↓"; }
.source-card[open] .source-toggle::after { content: "Show less ↑"; }

/* --- Typing indicator --- */
.typing-indicator {
    display: inline-flex; align-items: center; gap: 8px;
    color: #64748B; font-size: 14px; padding: 2px 0;
}
.typing-dots {
    display: inline-flex; gap: 5px; align-items: center;
}
.typing-dots span {
    width: 7px; height: 7px; background: #0E7C86; border-radius: 50%;
    animation: pulse 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
    0%, 60%, 100% { opacity: 0.3; transform: scale(0.85); }
    30% { opacity: 1; transform: scale(1); }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Feedback row buttons: subtle */
.stButton button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #E2E8F0 !important;
    color: #64748B !important;
    padding: 0.2rem 0.5rem !important;
    font-size: 13px !important;
    min-height: 28px !important;
}
.stButton button[kind="secondary"]:hover {
    background: #E6F4F5 !important;
    border-color: #0E7C86 !important;
    color: #0E7C86 !important;
}
</style>
"""

st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


def _log_feedback(message_id: str, question: str, answer: str, rating: str) -> None:
    is_new = not FEEDBACK_LOG.exists()
    with FEEDBACK_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "message_id", "rating", "question", "answer"])
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                message_id,
                rating,
                question,
                answer,
            ]
        )


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


def _tag_class(source: str) -> str:
    return {"FAQ": "faq", "TICKET": "ticket", "GUIDE": "guide"}.get(
        source.upper(), "guide"
    )


def _render_user_message(content: str) -> None:
    safe = html.escape(content).replace("\n", "<br>")
    st.markdown(
        f"""
<div class="user-msg">
  <div class="user-bubble">{safe}</div>
  <div class="chat-avatar user-avatar">👤</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_sources(docs) -> None:
    label = f"📚 Sources ({len(docs)})"
    with st.expander(label):
        for d in docs:
            source = str(d.metadata.get("source", "?"))
            source_id = str(d.metadata.get("source_id", "?"))
            body = html.escape(d.page_content).replace("\n", "<br>")
            tag_cls = _tag_class(source)
            st.markdown(
                f"""
<details class="source-card">
  <summary>
    <div class="source-head">
      <span class="source-tag {tag_cls}">{html.escape(source)}</span>
      <span class="source-id">{html.escape(source_id)}</span>
    </div>
    <div class="source-body">{body}</div>
    <span class="source-toggle"></span>
  </summary>
</details>
""",
                unsafe_allow_html=True,
            )


def _render_feedback(message_id: str, question: str, answer: str) -> None:
    rated_key = f"rated_{message_id}"
    if st.session_state.get(rated_key):
        st.caption(f"Feedback recorded: {st.session_state[rated_key]}")
        return
    col_up, col_down, _ = st.columns([1, 1, 10])
    if col_up.button("👍", key=f"up_{message_id}"):
        _log_feedback(message_id, question, answer, "up")
        st.session_state[rated_key] = "👍"
        st.rerun()
    if col_down.button("👎", key=f"down_{message_id}"):
        _log_feedback(message_id, question, answer, "down")
        st.session_state[rated_key] = "👎"
        st.rerun()


def _render_history() -> None:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            _render_user_message(msg["content"])
        else:
            with st.chat_message("assistant", avatar="📡"):
                st.markdown(msg["content"])
                if msg.get("docs"):
                    _render_sources(msg["docs"])
                _render_feedback(msg["id"], msg.get("question", ""), msg["content"])


def _handle_question(question: str) -> None:
    st.session_state.messages.append({"role": "user", "content": question})
    _render_user_message(question)

    with st.chat_message("assistant", avatar="📡"):
        placeholder = st.empty()
        placeholder.markdown(
            '<div class="typing-indicator">'
            '<span>NovaCell is typing</span>'
            '<span class="typing-dots"><span></span><span></span><span></span></span>'
            '</div>',
            unsafe_allow_html=True,
        )
        try:
            token_stream, docs = stream_answer(question)
        except RuntimeError as e:
            placeholder.error(str(e))
            return

        streamed = ""
        for token in token_stream:
            streamed += token
            placeholder.markdown(streamed + "▌")
        placeholder.markdown(streamed)
        _render_sources(docs)

        message_id = uuid.uuid4().hex
        st.session_state.messages.append(
            {
                "role": "assistant",
                "id": message_id,
                "content": streamed,
                "docs": docs,
                "question": question,
            }
        )
        _render_feedback(message_id, question, streamed)


def main() -> None:
    _init_state()

    with st.sidebar:
        st.markdown(
            f'<div class="sidebar-brand">{SIGNAL_LOGO_SVG}'
            f'<span class="brand-title">NovaCell Support</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Grounded answers from FAQ, resolved tickets, and user guides.")

        st.markdown(
            '<div class="sidebar-section">Sample questions</div>',
            unsafe_allow_html=True,
        )
        for i, q in enumerate(SAMPLE_QUESTIONS):
            if st.button(q, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

        # Pin "Clear conversation" to bottom of the sidebar
        st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)
        if st.button(
            "🗑️  Clear conversation",
            key="clear_btn",
            use_container_width=True,
            type="tertiary",
        ):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

    st.title("Ask NovaCell")
    st.caption(
        "Answers for data, billing, SIM/eSIM, roaming, voice, and account basics — "
        "grounded in NovaCell's own knowledge. For personal account details, call 611 "
        "or use the MyTelecom app."
    )

    _render_history()

    pending = st.session_state.pending_question
    typed = st.chat_input("Ask about data, billing, roaming, eSIM…")
    question = pending or typed
    if question:
        st.session_state.pending_question = None
        _handle_question(question)


if __name__ == "__main__":
    main()
