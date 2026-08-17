import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)  

app = FastAPI()

# FRONTEND_URL is set in Render to the public address of the Vite site.
# Multiple addresses can be separated by commas (for example, production and
# local development).
allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
