from fastapi import FastAPI
import uvicorn
from core.config import settings
from starlette.middleware.cors import CORSMiddleware
from api.router import api_router
from models import Base
from core.db import engine


Base.metadata.create_all(engine, checkfirst=True)
app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", workers=4)
