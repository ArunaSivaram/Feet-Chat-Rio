"""Ingest data/faq.csv into the `faq` Chroma collection (1 row = 1 document)."""
from __future__ import annotations

import csv

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import CHROMA_DIR, COLLECTION_FAQ, FAQ_CSV
from embeddings import get_embeddings


def load_faq_documents() -> list[Document]:
    docs: list[Document] = []
    with FAQ_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row_id = row["id"].strip()
            question = row["question"].strip()
            answer = row["answer"].strip()
            category = row["category"].strip()
            page_content = f"Q: {question}\nA: {answer}"
            docs.append(
                Document(
                    page_content=page_content,
                    metadata={
                        "source": "FAQ",
                        "source_id": f"FAQ-{row_id}",
                        "category": category,
                        "question": question,
                    },
                )
            )
    return docs


def main() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_FAQ in existing:
        client.delete_collection(COLLECTION_FAQ)

    docs = load_faq_documents()
    ids = [d.metadata["source_id"] for d in docs]

    Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_FAQ,
        persist_directory=str(CHROMA_DIR),
        ids=ids,
    )
    print(f"Ingested {len(docs)} FAQ documents into collection '{COLLECTION_FAQ}'.")


if __name__ == "__main__":
    main()
