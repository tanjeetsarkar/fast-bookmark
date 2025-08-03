from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "BookMarks"
    LOCAL_DB: str = "bookmarks.db"


settings = Settings()