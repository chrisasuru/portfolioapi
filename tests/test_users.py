from ..models.auth.user import User 
from ..models.auth.role import Role 
from ..models.auth.permission import Permission
from sqlmodel import select
from fastapi import status


def test_unathenticated_cannot_list_users(client):

    response = client.get("/v1/users")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_cannot_list_users(authenticated_client):

    response = authenticated_client.get("/v1/users")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_user_can_list_users(admin_authenticated_client):

    response = admin_authenticated_client.get("/v1/users")

    assert response.status_code == status.HTTP_200_OK

def test_super_admin_user_can_list_users(super_admin_authenticated_client):

    response = super_admin_authenticated_client.get("/v1/users")

    assert response.status_code == status.HTTP_200_OK


def test_unathenticated_can_create_user(session, client):

    user_data = {
        "username":"username",
        "email":"username@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_authenticated_cannot_create_user(session, authenticated_client):

    user_data = {
        "username":"username",
        "email":"username@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = authenticated_client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_user_can_create_user(session, admin_authenticated_client):

    user_data = {
        "username":"username",
        "email":"username@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = admin_authenticated_client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_super_admin_can_create_user(session, super_admin_authenticated_client):

    user_data = {
        "username":"username",
        "email":"username@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = super_admin_authenticated_client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_201_CREATED

 
def test_unathenticated_cannot_update_user(client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    updated_data = {
        "username":"updated_username"
    }

    response = client.put(endpoint, json = updated_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_can_update_own_user(authenticated_client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    updated_data = {
        "username":"updated_username"
    }

    response = authenticated_client.put(endpoint, json = updated_data)

    assert response.status_code == status.HTTP_200_OK



def test_user_cannot_update_other_user(session, authenticated_client, test_user):

    other_user = session.exec(select(User).where(User.id != test_user.id)).first()

    endpoint = f"/v1/users/{other_user.id}"

    updated_data = {
        "username":"updated_username"
    }

    response = authenticated_client.put(endpoint, json = updated_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_can_update_user(admin_authenticated_client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    updated_data = {
        "username":"updated_username"
    }

    response = admin_authenticated_client.put(endpoint, json = updated_data)

    assert response.status_code == status.HTTP_200_OK


def test_super_admin_can_update_user(super_admin_authenticated_client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    updated_data = {
        "username":"updated_username"
    }

    response = super_admin_authenticated_client.put(endpoint, json = updated_data)

    assert response.status_code == status.HTTP_200_OK

def test_unauthenticated_cannot_delete_user(client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    response = client.delete(endpoint)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_can_delete_own_user(authenticated_client, test_user):
    
    endpoint = f"/v1/users/{test_user.id}"

    response = authenticated_client.delete(endpoint)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_admin_can_delete_user(admin_authenticated_client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    response = admin_authenticated_client.delete(endpoint)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_super_admin_can_delete_user(super_admin_authenticated_client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    response = super_admin_authenticated_client.delete(endpoint)

    assert response.status_code == status.HTTP_204_NO_CONTENT  


