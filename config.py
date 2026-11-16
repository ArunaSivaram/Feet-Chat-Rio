from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / "chroma_store"

FAQ_CSV = DATA_DIR / "faq.csv"
TICKETS_DB = DATA_DIR / "tickets.db"
GUIDE_PDF = DATA_DIR / "telecom_guide.pdf"

COLLECTION_FAQ = "faq"
COLLECTION_TICKETS = "tickets"
COLLECTION_GUIDES = "guides"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

GUIDE_CHUNK_SIZE = 600
GUIDE_CHUNK_OVERLAP = 100

TOP_K_PER_COLLECTION = 3

GROQ_MODEL = "qwen/qwen3.8-27b"
GROQ_TEMPERATURE = 0
GROQ_REASONING_EFFORT = "none"

FEEDBACK_LOG = PROJECT_ROOT / "feedback_log.csv"
