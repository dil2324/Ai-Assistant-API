import os
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionSystemMessageParam
from typing import Final


load_dotenv()

OPENAI_API = os.getenv("OPENAI_API")

if OPENAI_API is None:
    raise RuntimeError("OPENAI_API not found")

_raw_database_url = os.getenv("DATABASE_URL") or ""

if not _raw_database_url:
    raise RuntimeError("DATABASE_URL not found")

# Render (and Heroku-style providers) hand out connection strings as
# "postgres://..." or plain "postgresql://...". SQLAlchemy needs the driver
# named explicitly in the scheme to know which DBAPI to use, so we normalize
# to "postgresql+psycopg://..." here instead of forcing a module override
# in database.py (which risked mismatched dialect/DBAPI behavior).

if _raw_database_url.startswith("postgres://"):
    _raw_database_url = _raw_database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif _raw_database_url.startswith("postgresql://") and "+psycopg" not in _raw_database_url:
    _raw_database_url = _raw_database_url.replace("postgresql://", "postgresql+psycopg://", 1)

DATABASE_URL: Final[str] = _raw_database_url

MAX_HISTORY = 10

SYSTEM_PROMPT: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": "You're an AI assistant chat. Answer me briefly and to the point"
}