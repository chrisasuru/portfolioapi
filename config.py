import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Settings:

    DATABASE_URL: str = DATABASE_URL
    DEBUG: bool = os.getenv("DEBUG") == "TRUE"
    LOG_SQL_QUERIES: bool = os.getenv("LOG_SQL_QUERIES") == "TRUE"
    DEFAULT_PAGE_SIZE: int = 20
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEFAULT_USER_ROLE: str = "user"
    SUPER_ADMIN_USER_ROLE: str = "super_admin"
    ADMIN_USER_ROLE: str = 'admin'
    RESERVED_USERNAMES: str = ['admin', 'user', 'test', 'root', 'super_user'],
    DEFAULT_BLOG_CATEGORIES: list = ['JavaScript', 'Python', 'Object Oriented Programming', 'SaaS', 'Testing', 'C', 'C Sharp', 'TypeScript', 'Compiler']
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20

settings = Settings()
