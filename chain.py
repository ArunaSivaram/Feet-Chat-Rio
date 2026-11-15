"""LCEL chain: merged retrieval -> prompt -> Groq Qwen -> string output.

If no doc clears MIN_RELEVANCE, the chain short-circuits with the canned
NO_ANSWER_TEXT and the LLM is never called.
"""
from __future__ import annotations

import os
from typing import Iterator

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from config import (
    GROQ_MODEL,
    GROQ_REASONING_EFFORT,
    GROQ_TEMPERATURE,
    NO_ANSWER_TEXT,
)
from retriever import format_context, retrieve

SYSTEM_PROMPT = """You are NovaCell's telecom support assistant.

Rules you must follow:
1. Answer ONLY using facts that appear in the provided Context. Do not use any outside knowledge, memorized facts, prices, or policies.
2. If the Context does not contain a reliable answer, reply exactly:
   "{no_answer}"
3. Be concise and practical. Use plain language. Prefer numbered steps when giving instructions.
4. Do not invent prices, phone numbers, URLs, SLAs, or policy terms.
5. Never claim to see the user's account, balance, or bill.

Context (each block is labelled with its source and relevance score):
{context}
"""

USER_PROMPT = "{question}"

_prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
).partial(no_answer=NO_ANSWER_TEXT)


def _make_llm() -> ChatGroq:
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=GROQ_TEMPERATURE,
        reasoning_effort=GROQ_REASONING_EFFORT,
    )


def _fallback_stream() -> Iterator[str]:
    yield NO_ANSWER_TEXT


def answer(question: str) -> dict:
    """Return {'answer': str, 'docs': list[Document]} for a one-shot question."""
    docs = retrieve(question)
    if not docs:
        return {"answer": NO_ANSWER_TEXT, "docs": []}
    context = format_context(docs)
    llm = _make_llm()
    out = (_prompt | llm | StrOutputParser()).invoke(
        {"context": context, "question": question}
    )
    return {"answer": out, "docs": docs}


def stream_answer(question: str) -> tuple[Iterator[str], list[Document]]:
    """Return (token_iterator, retrieved_docs) for streaming UIs.

    Short-circuits to the canned fallback when nothing clears MIN_RELEVANCE.
    """
    docs = retrieve(question)
    if not docs:
        return _fallback_stream(), []
    context = format_context(docs)
    llm = _make_llm()
    stream = (_prompt | llm | StrOutputParser()).stream(
        {"context": context, "question": question}
    )
    return stream, docs
