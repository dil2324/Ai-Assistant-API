from sqlalchemy.orm import Session
from typing import cast
from openai.types.chat import ChatCompletionMessageParam
from app.models import Message

def clear_history(db: Session,user_id: str):
    db.query(Message).filter(Message.user_id == user_id).delete()
    db.commit()
    

def get_history(db: Session,user_id: str) -> list[ChatCompletionMessageParam]:
    messages = (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.id)
        .all()
    )
    
    history: list[ChatCompletionMessageParam] = []
    
    for msg in messages:
        history.append(
            cast(
                ChatCompletionMessageParam,
                {
                    "role": msg.role,
                    "content": msg.content,
                },
            )
        )
    
    return history

def save_message(db: Session,user_id: str,role: str,content: str,):
    message = Message(
        user_id = user_id,
        role = role,
        content = content
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
