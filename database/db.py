from sqlmodel import create_engine, Session
from ..config import settings
from ..models.auth.user import User
from ..models.auth.permission import Permission
from ..models.auth.role import Role
from ..models.blog.tag import BlogTag
from ..models.blog.comment import BlogComment
from ..models.blog.post import BlogPost

from .setup import RBACInitializer, BlogInitializer



engine = create_engine(
    settings.DATABASE_URL, 
    echo = settings.LOG_SQL_QUERIES,
    connect_args={"check_same_thread": False} if settings.DEBUG else None
)


def init_db():

    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    RBACInitializer(Session(engine)).populate()
    BlogInitializer(Session(engine)).populate()


def destroy_db():

    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(engine)


def get_session():

    with Session(engine) as session:

        yield session
