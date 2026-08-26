import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
from app.schemas import ChatRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import client
from app.config import SYSTEM_PROMPT, MAX_HISTORY
from app.crud import save_message, get_history, clear_history
from app.database import SessionLocal
from app.models import User
from app.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.limiter import limiter
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionUserMessageParam

router = APIRouter()


def get_db() -> Generator["Session", None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: "Session" = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> User:
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_id = int(payload["sub"])
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


@router.get("/")
async def root():
    return {
        "name": "AI Chat API",
        "status": "running",
        "docs": "/docs"
    }


@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(
    request: Request, body: RegisterRequest, db: "Session" = Depends(get_db)
) -> TokenResponse:
    existing_user = db.query(User).filter(User.username == body.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=body.username, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request, body: LoginRequest, db: "Session" = Depends(get_db)
) -> TokenResponse:
    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=current_user.id, username=current_user.username)


@router.post("/chat")
@limiter.limit("5/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: "Session" = Depends(get_db),
):
    user_id = str(current_user.id)
    history = get_history(db, user_id)

    user_msg: ChatCompletionUserMessageParam = {"role": "user", "content": body.message}

    try:
        messages_to_send: list[ChatCompletionMessageParam] = [
            SYSTEM_PROMPT,
            *history[-(MAX_HISTORY - 1):],
            user_msg,
        ]
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send
        )

        gpt_answer = response.choices[0].message.content or "Something went wrong"
        save_message(db, user_id, "user", body.message)
        save_message(
            db,
            user_id,
            "assistant",
            gpt_answer
        )

        return {"answer": gpt_answer}

    except Exception as e:
        logging.error(f"OPENAI error for user {user_id}: {e} ")
        raise HTTPException(status_code=500, detail="API error")

@router.post("/clear")
async def clear(
    current_user: User = Depends(get_current_user),
    db: "Session" = Depends(get_db),
):
    clear_history(db, str(current_user.id))
    return {"status": "cleared"}