"""Ingest data/tickets.db resolved tickets into the `tickets` Chroma collection."""
from __future__ import annotations

import sqlite3

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import CHROMA_DIR, COLLECTION_TICKETS, TICKETS_DB
from embeddings import get_embeddings


def load_ticket_documents() -> list[Document]:
    con = sqlite3.connect(TICKETS_DB)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            "SELECT ticket_id, category, issue_type, description, resolution "
            "FROM tickets WHERE status = 'resolved'"
        ).fetchall()
    finally:
        con.close()

    docs: list[Document] = []
    for row in rows:
        page_content = (
            f"Issue: {row['issue_type']}\n"
            f"Description: {row['description']}\n"
            f"Resolution: {row['resolution']}"
        )
        docs.append(
            Document(
                page_content=page_content,
                metadata={
                    "source": "TICKET",
                    "source_id": row["ticket_id"],
                    "category": row["category"],
                    "issue_type": row["issue_type"],
                },
            )
        )
    return docs


def main() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_TICKETS in existing:
        client.delete_collection(COLLECTION_TICKETS)

    docs = load_ticket_documents()
    ids = [d.metadata["source_id"] for d in docs]

    Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_TICKETS,
        persist_directory=str(CHROMA_DIR),
        ids=ids,
    )
    print(f"Ingested {len(docs)} resolved tickets into collection '{COLLECTION_TICKETS}'.")


if __name__ == "__main__":
    main()
