from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from core.config import settings

SQLLITE_DB = settings.LOCAL_DB

engine = create_engine(f"sqlite:///{SQLLITE_DB}")

def get_db():
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]