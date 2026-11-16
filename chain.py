"""LCEL chain: merged retrieval -> prompt -> Groq Qwen -> string output."""
from __future__ import annotations

import os
from typing import Iterator

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_groq import ChatGroq

from config import GROQ_MODEL, GROQ_REASONING_EFFORT, GROQ_TEMPERATURE
from retriever import format_context, retrieve

load_dotenv()

SYSTEM_PROMPT = """You are NovaCell's telecom support assistant.

Rules you must follow:
1. Answer ONLY using facts that appear in the provided Context. Do not use any outside knowledge, memorized facts, prices, or policies.
2. If the Context does not contain a reliable answer, reply exactly:
   "I don't have a reliable answer for that in my current knowledge. For help, please call 611 or use the MyTelecom app."
3. Be concise and practical. Use plain language. Prefer numbered steps when giving instructions.
4. Do not invent prices, phone numbers, URLs, SLAs, or policy terms.
5. Never claim to see the user's account, balance, or bill.

Context (each block is labelled with its source):
{context}
"""

USER_PROMPT = "{question}"

_prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
)


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


def _retrieve_docs(payload: dict) -> list[Document]:
    return retrieve(payload["question"])


def build_chain():
    llm = _make_llm()
    retrieve_runnable = RunnableLambda(_retrieve_docs)
    return (
        RunnablePassthrough.assign(docs=retrieve_runnable)
        .assign(context=lambda p: format_context(p["docs"]))
        | RunnablePassthrough.assign(
            answer=_prompt | llm | StrOutputParser()
        )
    )


def answer(question: str) -> dict:
    """Return {'answer': str, 'docs': list[Document]} for a one-shot question."""
    chain = build_chain()
    result = chain.invoke({"question": question})
    return {"answer": result["answer"], "docs": result["docs"]}


def stream_answer(question: str) -> tuple[Iterator[str], list[Document]]:
    """Return (token_iterator, retrieved_docs) for streaming UIs.

    Retrieval runs once up-front so the UI can render Sources immediately.
    """
    docs = retrieve(question)
    context = format_context(docs)
    llm = _make_llm()
    stream = (_prompt | llm | StrOutputParser()).stream(
        {"context": context, "question": question}
    )
    return stream, docs
