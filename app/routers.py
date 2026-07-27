import logging
from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest
from app.services import client
from app.config import SYSTEM_PROMPT, MAX_HISTORY
from app.crud import save_message, get_history, clear_history
from app.database import SessionLocal
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam

router = APIRouter()



@router.get("/")
async def root():
    return {
        "name": "AI Chat API",
        "status": "running",
        "docs": "/docs"
    }
    
@router.post("/chat")
async def chat(request: ChatRequest):
    
    user_id= request.user_id
    db = SessionLocal()
    history = get_history(db, user_id)
    
    if not history:
        history.append(SYSTEM_PROMPT)
        
    history.append(
        {
            "role": "user",
            "content": request.message
        }
    )
        
    user_msg : ChatCompletionUserMessageParam = {"role": "user","content": request.message}
    history.append(user_msg)

    save_message(
        db,
        user_id,
        "user",
        request.message
    )
        
    try:
        messages_to_send = history[-MAX_HISTORY:]
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send
        )
        
        gpt_answer = response.choices[0].message.content or "Something went wrong"
        assistant_msg : ChatCompletionAssistantMessageParam = {"role": "assistant", "content": gpt_answer}
        history.append(assistant_msg)
        
        save_message(
            db,
            user_id,
            "assistant",
            gpt_answer
        )
        
        return {"answer": gpt_answer}
    
    except Exception as e:
        logging.error(f"OPENAI error for user {user_id}: {e} ")
        raise HTTPException(status_code=500,detail="API error")
    
    finally:
        db.close()
    
@router.post("/clear")
async def clear(request: ChatRequest):
    db = SessionLocal()
    
    try:
        clear_history(db,request.user_id)
        return {"status": "cleared"}
    finally:
        db.close()
    