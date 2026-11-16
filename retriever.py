"""Merged retriever: top-K from each of the three Chroma collections."""
from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import (
    CHROMA_DIR,
    COLLECTION_FAQ,
    COLLECTION_GUIDES,
    COLLECTION_TICKETS,
    TOP_K_PER_COLLECTION,
)
from embeddings import get_embeddings

_COLLECTIONS = (COLLECTION_FAQ, COLLECTION_TICKETS, COLLECTION_GUIDES)


def _vectorstore(collection_name: str) -> Chroma:
    return Chroma(
        collection_name=collection_name,
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


def retrieve(query: str, k: int = TOP_K_PER_COLLECTION) -> list[Document]:
    results: list[Document] = []
    for name in _COLLECTIONS:
        store = _vectorstore(name)
        results.extend(store.similarity_search(query, k=k))
    return results


def format_context(docs: list[Document]) -> str:
    blocks = []
    for d in docs:
        label = f"[{d.metadata.get('source', 'UNKNOWN')} · {d.metadata.get('source_id', '?')}]"
        blocks.append(f"{label}\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)
