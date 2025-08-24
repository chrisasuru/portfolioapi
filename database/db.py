from sqlmodel import create_engine, Session
from ..config import settings
from ..models.user import Permission, Role, User
from .init import RBACInitializer



engine = create_engine(
    settings.DATABASE_URL, 
    echo = settings.DEBUG
)


def init_db():

    from sqlmodel import SQLModel
    from ..models.user import User

    SQLModel.metadata.create_all(engine)

    permission_initializer = RBACInitializer(Session(engine))
    permission_initializer.create_permissions()
    permission_initializer.create_roles()
    permission_initializer.create_super_admin()


def destroy_db():

    from sqlmodel import SQLModel
    from ..models.user import User
    SQLModel.metadata.drop_all(engine)


def get_session():

    with Session(engine) as session:

        yield session
