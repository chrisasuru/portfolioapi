from ..models.authentication.models import User, Role, Permission
from ..core import utils
from fastapi import status


def test_create_user(session, client):

    user_data = {
        "username":"username",
        "email":"username@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_create_user_authenticated(session, authenticated_client):

    user_data = {
        "username":"username",
        "email":"username@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = authenticated_client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
 