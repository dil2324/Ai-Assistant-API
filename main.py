import logging
import os
from fastapi import FastAPI,HTTPException
from collections import defaultdict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam

logging.basicConfig(level=logging.INFO)

load_dotenv()
OPENAI_API = os.getenv("OPENAI_API")

if OPENAI_API is None:
    raise RuntimeError("OPENAI_API not found")

app = FastAPI(title="AI chat API")
client = AsyncOpenAI(api_key = OPENAI_API)

user_histories: dict[str, list[ChatCompletionMessageParam]] = defaultdict(list)
MAX_HISTORY = 10
SYSTEM_PROMPT: ChatCompletionSystemMessageParam = {"role": "system", "content": "You're an AI Assistant chat. Answer me briefly and to the point "}

class ChatRequest(BaseModel):
    user_id: str =Field (
        min_length = 3,
        max_length = 32,
        pattern = r"^[a-zA-z0-9_-]+$"
        
    )
    message: str = Field (
        min_length = 1,
        max_length = 2000,
        
    )

@app.get("/")
async def open():
    return {
        "name": "AI chat API",
        "status": "running",
        "docs": "/docs"
    }

    
@app.post("/chat")
async def chat(request: ChatRequest):
    
    user_id = request.user_id
    
    if not user_histories[user_id]:
        user_histories[user_id].append(SYSTEM_PROMPT)
        
    user_msg: ChatCompletionUserMessageParam = {"role":"user","content": request.message}
    user_histories[user_id].append(user_msg)
    
    try:
        messages_to_send = user_histories[user_id][-MAX_HISTORY:]
        response = await client.chat.completions.create(
            model= "gpt-4o-mini",
            messages = messages_to_send
        )
        gpt_answer = response.choices[0].message.content or "Something went wrong"
        assistant_msg: ChatCompletionAssistantMessageParam = {"role":"assistant","content": gpt_answer}
        user_histories[user_id].append(assistant_msg)
        
        return {"answer": gpt_answer}
        
    
    except Exception as e:
        logging.error(f"OpenAI error for user {user_id}: {e}")
        raise HTTPException(status_code=500,detail="API error")
    
@app.post("/clear")
async def clear(request: ChatRequest):
    user_histories[request.user_id] = [SYSTEM_PROMPT]
    return {"status": "cleared"}