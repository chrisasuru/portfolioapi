import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Settings:

    DATABASE_URL: str = DATABASE_URL
    DEBUG: str = os.getenv("DEBUG") == "TRUE"
    DEFAULT_PAGE_SIZE: int = 20
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEFAULT_ROLE: str = "user"
    SUPER_ADMIN_ROLE: str = "super_admin"


settings = Settings()
