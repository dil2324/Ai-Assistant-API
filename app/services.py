from openai import AsyncOpenAI
from app.config import OPENAI_API

client = AsyncOpenAI(api_key = OPENAI_API)