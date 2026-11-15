"""Merged retriever: top-K from each Chroma collection, filtered by MIN_RELEVANCE."""
from __future__ import annotations

import math

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import (
    CHROMA_DIR,
    COLLECTION_FAQ,
    COLLECTION_GUIDES,
    COLLECTION_TICKETS,
    MIN_RELEVANCE,
    TOP_K,
)
from embeddings import get_embeddings

_COLLECTIONS = (COLLECTION_FAQ, COLLECTION_TICKETS, COLLECTION_GUIDES)
_SQRT2 = math.sqrt(2.0)


def _vectorstore(collection_name: str) -> Chroma:
    return Chroma(
        collection_name=collection_name,
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


def _relevance_from_distance(distance: float) -> float:
    # Chroma's default L2 on normalised embeddings; mirrors langchain's
    # default cosine-relevance formula, clamped to [0, 1].
    sim = 1.0 - distance / _SQRT2
    return max(0.0, min(1.0, sim))


def retrieve(
    query: str,
    k: int = TOP_K,
    min_relevance: float = MIN_RELEVANCE,
) -> list[Document]:
    """Return docs from all 3 collections whose relevance >= min_relevance.

    Each returned doc carries its score in metadata["relevance_score"].
    """
    results: list[Document] = []
    for name in _COLLECTIONS:
        store = _vectorstore(name)
        pairs = store.similarity_search_with_score(query, k=k)
        for doc, distance in pairs:
            relevance = _relevance_from_distance(float(distance))
            if relevance >= min_relevance:
                doc.metadata["relevance_score"] = round(relevance, 3)
                results.append(doc)
    return results


def format_context(docs: list[Document]) -> str:
    blocks = []
    for d in docs:
        score = d.metadata.get("relevance_score")
        score_tag = f" (score {score})" if score is not None else ""
        label = (
            f"[{d.metadata.get('source', 'UNKNOWN')} · "
            f"{d.metadata.get('source_id', '?')}{score_tag}]"
        )
        blocks.append(f"{label}\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)
