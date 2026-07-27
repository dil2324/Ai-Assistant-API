import os
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionSystemMessageParam
from typing import Final


load_dotenv()

OPENAI_API = os.getenv("OPENAI_API")

if OPENAI_API is None:
    raise RuntimeError("OPENAI_API not found")

DATABASE_URL: Final[str]= os.getenv("DATABASE_URL") or ""

if not DATABASE_URL :
    raise RuntimeError("DATABASE_URL not found")

 
MAX_HISTORY = 10

SYSTEM_PROMPT: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": "You're an AI assistant chat. Answer me briefly and to the point"
}