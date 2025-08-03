from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from datetime import datetime

from sqlalchemy import func, insert, select
from core.db import SessionDep
from models import BookMarks


router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


class BookmarkBase(BaseModel):
    label: Optional[str]
    url: AnyHttpUrl


class BookmarkPublic(BookmarkBase):
    id: int
    date_created: datetime
    date_modified: datetime

    class Config:
        orm_model = True


class BookmarksPublic(BaseModel):
    data: List[BookmarkPublic]
    count: int

class BookMarkDelete(BaseModel):
    id: Optional[int]
    all: Optional[bool]

@router.get("/", response_model=BookmarksPublic)
def read_items(*, db: SessionDep) -> Any:
    count_st = select(func.count()).select_from(BookMarks)
    count = db.execute(count_st).scalar_one()
    st = select(BookMarks)

    bookmarks = db.execute(st).scalars().all()
    bookmarks = [BookmarkPublic(**row.__dict__) for row in bookmarks]
    return BookmarksPublic(data=bookmarks, count=count)


@router.post("/", response_model=BookmarkPublic)
def create_item(*, db: SessionDep, bookmark: BookmarkBase) -> Any:
    bm = db.query(BookMarks).filter(BookMarks.url == bookmark.url.encoded_string()).first()

    if bm:
        raise HTTPException(409, f"[Server Error] Bookmark with label: {bm.label} already exists for {bm.url}")
    
    stmt = (
        insert(BookMarks)
        .values(label=bookmark.label, url=bookmark.url.encoded_string())
        .returning("*")
    )
    result = db.execute(stmt)
    new_bookmark = result.fetchone()
    db.commit()
    return new_bookmark

@router.delete("/{id}")
def delete_item(*, db:SessionDep, id: int) -> str:
    
    bm = db.get(BookMarks, id)

    if not bm:
        raise HTTPException(404, detail="Bookmark not found")
    db.delete(bm)
    db.commit()

    return f"Bookmark Deleted: ID: {bm.id}\t label: {bm.label}\t url: {bm.url}"

