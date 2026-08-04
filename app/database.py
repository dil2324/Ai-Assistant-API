from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

print("DATABASE_URL=", DATABASE_URL)
engine = create_engine(DATABASE_URL,module=__import__("psycopg"))

SessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind=engine
)

class Base(DeclarativeBase):
    pass