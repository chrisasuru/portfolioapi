import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from ..database.db import get_session
from ..core.auth.dependecies import get_current_user
from ..database.setup import RBACInitializer
from ..database.setup import BlogInitializer
from sqlmodel.pool import StaticPool
from ..main import app


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
SQLModel.metadata.create_all(engine)


session = Session(engine)


rbac = RBACInitializer(session)
rbac.populate()
blog = BlogInitializer(session)
blog.populate()

test_user = rbac.create_basic_user(
    username = "testuser",
    email = "testuser@example.com",
    password = "password"
)


other_user = rbac.create_basic_user(
    username = "otheruser",
    email = "otheruser@example.com",
    password = "password"
)

test_admin_user = rbac.create_admin_user(
    username = 'admin_user_test', 
    email = 'admin_user_test@example.com',
    password = 'password'
)


test_super_admin_user = rbac.create_super_admin_user(
    username = 'super_admin_user_test', 
    email = 'super_admin_user_test@example.com',
    password = 'password'
)

test_delete_user = rbac.create_basic_user(
    username = 'delete_user_test', 
    email = 'delete_user_test@example.com',
    password = 'password'
)

test_editor_user = rbac.create_editor_user()
test_publisher_user = rbac.create_publisher_user()



@pytest.fixture(name="session")
def session_fixture():
    # Setup: Create test database

    yield session  # Pass this session to tests

@pytest.fixture(name = "rbac")
def rbac_fixture(session):

    rbac = RBACInitializer(session)

    return rbac
    
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
def test_user_fixture():

    return test_user


@pytest.fixture(name="test_delete_user")
def test_delete_user_fixture():

    return test_delete_user

@pytest.fixture(name="test_other_user")
def test_other_user_fixture():

    return other_user





@pytest.fixture(name = "authenticated_client")
def authenticated_client_fixture(session):

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

    return test_admin_user

@pytest.fixture(name = "test_super_admin_user")
def test_super_admin_user_fixture(session):

    return test_super_admin_user




@pytest.fixture(name = "admin_authenticated_client")
def test_admin_authenticated_client_fixture(session):

    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_admin_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name = "super_admin_authenticated_client")
def test_super_admin_authenticated_client_fixture(session):

    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_super_admin_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()

@pytest.fixture(name="publisher_authenticated_client")
def test_publisher_authenticated_client_fixture(session):
    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_publisher_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(name="editor_authenticated_client")
def test_editor_authenticated_client_fixture(session):
    def get_session_override():

        return session
    
    def get_current_user_override():

        return test_editor_user
    

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()