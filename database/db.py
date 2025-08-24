from sqlmodel import create_engine, Session
from ..config import settings
from ..models.authentication.models import Permission, Role, User
from .setup import RBACInitializer



engine = create_engine(
    settings.DATABASE_URL, 
    echo = settings.DEBUG
)


def init_db():

    from sqlmodel import SQLModel
    from ..models.authentication.models import User, Role, Permission

    SQLModel.metadata.create_all(engine)

    RBACInitializer(Session(engine)).populate()


def destroy_db():

    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(engine)


def get_session():

    with Session(engine) as session:

        yield session
