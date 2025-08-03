from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

SQLLITE_DB = "bookmarks.db"

engine = create_engine(f"sqlite:///{SQLLITE_DB}", echo=True)

def get_db():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]