import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env_str(key: str, default: str) -> str:
    v = os.getenv(key)
    return v if v else default


def _env_int(key: str, default: int) -> int:
    v = os.getenv(key)
    return int(v) if v else default


def _env_float(key: str, default: float) -> float:
    v = os.getenv(key)
    return float(v) if v else default


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / "chroma_store"

FAQ_CSV = DATA_DIR / "faq.csv"
TICKETS_DB = DATA_DIR / "tickets.db"
GUIDE_PDF = DATA_DIR / "telecom_guide.pdf"

COLLECTION_FAQ = "faq"
COLLECTION_TICKETS = "tickets"
COLLECTION_GUIDES = "guides"

EMBEDDING_MODEL = _env_str(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

GUIDE_CHUNK_SIZE = 600
GUIDE_CHUNK_OVERLAP = 100

TOP_K = _env_int("TOP_K", 3)
MIN_RELEVANCE = _env_float("MIN_RELEVANCE", 0.35)

GROQ_MODEL = _env_str("GROQ_MODEL", "qwen/qwen3.8-27b")
GROQ_TEMPERATURE = 0
GROQ_REASONING_EFFORT = "none"

FEEDBACK_LOG = PROJECT_ROOT / "feedback_log.csv"

NO_ANSWER_TEXT = (
    "I don't have a reliable answer for that in my current knowledge. "
    "For help, please call 611 or use the MyTelecom app."
)
