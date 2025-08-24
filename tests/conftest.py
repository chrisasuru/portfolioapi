import pytest
from fastapi.testclient import TestClient
from ..main import app
from sqlmodel import create_engine, Session, SQLModel
from ..models.authentication.user import User, Permission, ResourcePermission, Role
from ..database.db import get_session
from ..database.setup import RBACInitializer

TEST_DATABASE_URL = "sqlite:///./test.db" 


engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo = True
)


def get_test_session(engine):

    with Session(engine) as session:

        yield session

app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(scope="function")
def setup_test_db():
    # Create tables before each test
    SQLModel.metadata.create_all(engine)
    RBACInitializer(get_test_session(engine)).populate()
    yield
    # Drop tables after each test
    SQLModel.metadata.drop_all(bind=engine)

client = TestClient(app)


