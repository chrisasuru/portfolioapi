import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from ..database.db import get_session
from ..core.security import get_authenticated_user
from ..database.setup import RBACInitializer
from ..models.authentication.models import User, Role, Permission
from sqlmodel.pool import StaticPool
from ..core import utils
from ..main import app




@pytest.fixture(name="session")
def session_fixture():
    # Setup: Create test database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    
    with Session(engine) as session:

        rbac = RBACInitializer(session)
        rbac.populate()
        yield session  # Pass this session to tests
    
@pytest.fixture(name="client")
def client_fixture(session):

    def get_session_override():

        return session
    
    def get_authenticated_user_override():

        return None
    
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_authenticated_user] = get_authenticated_user_override

    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):

    rbac = RBACInitializer(session)
    rbac.populate()  # This should create default roles
    
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com", 
        password= utils.hash_password('password'),
        first_name="Test",
        last_name="User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@pytest.fixture(name = "authenticated_client")
def authenticated_client_fixture(session, test_user):

    def get_session_override():

        return session
    
    def get_authenticated_user_override():

        return test_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_authenticated_user] = get_authenticated_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()

