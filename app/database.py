from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

# pool_pre_ping checks that a pooled connection is still alive before using
# it. Render's Postgres (and most managed Postgres) silently drop idle
# connections after a while; without this you'd intermittently get
# "SSL connection has been closed unexpectedly" errors on the first query
# after any period of low traffic.

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind=engine
)

class Base(DeclarativeBase):
    pass
