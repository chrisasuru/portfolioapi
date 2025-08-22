from sqlmodel import create_engine
from .config import settings


engine = create_engine(
    settings.DATABASE_URL, 
    echo = settings.DEBUG
)


def init_db():

    from sqlmodel import SQLModel
    from .models.user import User

    SQLModel.metadata.create_all(engine)