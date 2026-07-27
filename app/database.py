from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind=engine
)

class Base(DeclarativeBase):
    pass