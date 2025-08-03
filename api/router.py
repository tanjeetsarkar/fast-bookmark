from fastapi import APIRouter

from api import bookmarks



api_router = APIRouter()

api_router.include_router(bookmarks.router)