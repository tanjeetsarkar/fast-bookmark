from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "BookMarks"


settings = Settings()