from sqlmodel import create_engine, Session
from ..config import settings
from ..models.auth.user import User
from ..models.auth.permission import Permission
from ..models.auth.role import Role
from .setup import RBACInitializer



engine = create_engine(
    settings.DATABASE_URL, 
    echo = settings.DEBUG,
    connect_args={"check_same_thread": False} if settings.DEBUG else None
)


def init_db():

    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    RBACInitializer(Session(engine)).populate()


def destroy_db():

    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(engine)


def get_session():

    with Session(engine) as session:

        yield session
