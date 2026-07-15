import logging
import os
from fastapi import FastAPI,HTTPException
from collections import defaultdict
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam

logging.basicConfig(level=logging.INFO)

load_dotenv()
OPENAI_API = os.getenv("OPENAI_API")

app = FastAPI(title="AI chat API")
client = AsyncOpenAI(api_key = OPENAI_API)

user_histoires: [dict, list[ChatCompletionMessageParam]] = defaultdict(list)
MAX_HISTORY = 10
SYSTEM_PROMPT = {"role": "system", "content": "You're an AI Assistant chat. Answer me briefly and to the point "}

class ChatRequest(BaseModel):
    user_id: str
    message: str
    
@app.post("/chat")
async def chat(request: ChatRequest):
    
    user_id = request.user_id
    
    if not user_histories[user_id]:
        user_histories[user_id].append(SYSTEM_PROMPT)
        
    user_msg: ChatCompletionUserMessageParam = {"role":"user","content": request.message}
    user_histories[user_id].append(user_msg)
    
    try:
        messages_to_send = user_histories[user_id][-MAX_HISTORY:]
    
    except: