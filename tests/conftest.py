import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel, select
from ..database.db import get_session
from ..core.security import get_current_user
from ..database.setup import RBACInitializer
from ..models.auth.user import User 
from ..models.auth.role import Role
from ..models.auth.permission import Permission
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
    
    def get_current_user_override():

        return None
    
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):

    rbac = RBACInitializer(session)
    rbac.populate()  # This should create default roles
    
    # Create test user

    user = rbac.create_basic_user(
        username = "testuser",
        email = "testuser@example.com",
        password = "password"
    )
    
    return user


@pytest.fixture(name = "authenticated_client")
def authenticated_client_fixture(session, test_user):

    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name="test_admin_user")
def test_admin_user_fixture(session):

    rbac = RBACInitializer(session)
    rbac.populate()

    admin_user = rbac.create_admin_user(
        username = 'admin_user_test', 
        email = 'admin_user_test@example.com',
        password = 'password'
    )


    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)

    return admin_user

@pytest.fixture(name = "test_super_admin_user")
def test_super_admin_user_fixture(session):

    rbac = RBACInitializer(session)
    rbac.populate()

    super_admin_user = rbac.create_super_admin_user(
        username = 'super_admin_user_test', 
        email = 'super_admin_user_test@example.com',
        password = 'password'
    )


    session.add(super_admin_user)
    session.commit()
    session.refresh(super_admin_user)

    return super_admin_user




@pytest.fixture(name = "admin_authenticated_client")
def test_admin_authenticated_client_fixture(session, test_admin_user):

    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_admin_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name = "super_admin_authenticated_client")
def test_super_admin_authenticated_client_fixture(session, test_super_admin_user):

    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_super_admin_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()




