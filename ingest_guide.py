"""Ingest data/telecom_guide.pdf into the `guides` Chroma collection (600/100 chunks)."""
from __future__ import annotations

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHROMA_DIR,
    COLLECTION_GUIDES,
    GUIDE_CHUNK_OVERLAP,
    GUIDE_CHUNK_SIZE,
    GUIDE_PDF,
)
from embeddings import get_embeddings


def load_guide_documents() -> list[Document]:
    loader = PyPDFLoader(str(GUIDE_PDF))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=GUIDE_CHUNK_SIZE,
        chunk_overlap=GUIDE_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    for i, chunk in enumerate(chunks):
        page = chunk.metadata.get("page")
        chunk.metadata = {
            "source": "GUIDE",
            "source_id": f"GUIDE-p{page}-c{i}" if page is not None else f"GUIDE-c{i}",
            "page": page,
        }
    return chunks


def main() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_GUIDES in existing:
        client.delete_collection(COLLECTION_GUIDES)

    docs = load_guide_documents()
    ids = [d.metadata["source_id"] for d in docs]

    Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_GUIDES,
        persist_directory=str(CHROMA_DIR),
        ids=ids,
    )
    print(f"Ingested {len(docs)} guide chunks into collection '{COLLECTION_GUIDES}'.")


if __name__ == "__main__":
    main()
