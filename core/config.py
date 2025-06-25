from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ENCRYPT_SECRET: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GITHUB_REDIRECT_URI: str
    MICROSOFT_REDIRECT_URI: str

    class Config:
        env_file = ".env"

settings = Settings()
