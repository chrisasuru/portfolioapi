from ..models.auth.user import User
from sqlmodel import select
from fastapi import status


def test_username_must_be_unique(client, test_user):

    user_data = {
        "username": test_user.username,
        "email": "random@example.com",
        "password": "password",
        "confirm_password": "password"
    }

    response = client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_email_must_be_unique(client, test_user):

    user_data = {
        "username": "random",
        "email": test_user.email,
        "password": "password",
        "confirm_password": "password"
    }

    response = client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_unique_pass_if_user_username(authenticated_client, test_user):

    user_data = {
        "username": test_user.username
    }

    response = authenticated_client.put(f"/v1/users/{test_user.id}", json = user_data)

    assert response.status_code == status.HTTP_200_OK

def test_unique_pass_if_user_email(authenticated_client, test_user):

    user_data = {
        "email": test_user.email
    }

    response = authenticated_client.put(f"/v1/users/{test_user.id}", json = user_data)

    assert response.status_code == status.HTTP_200_OK
 

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
        "username":"unauthenticated",
        "email":"unauthenticated@example.com",
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
        "username":"admin_can_create_username",
        "email":"admincancreateemail@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = admin_authenticated_client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_super_admin_can_create_user(session, super_admin_authenticated_client):

    user_data = {
        "username":"superadmincreate",
        "email":"superadmincreate@example.com",
        "password":"password",
        "confirm_password":"password"
    }

    response = super_admin_authenticated_client.post("/v1/users", json = user_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_unauthenticated_user_cannot_read_user(client, test_user):

    response = client.get(f"/v1/users/{test_user.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_can_read_self(authenticated_client, test_user):

    response = authenticated_client.get(f"/v1/users/{test_user.id}")

    assert response.status_code == status.HTTP_200_OK
 
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
        "username":"update_own_username"
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



def test_admin_can_update_user(admin_authenticated_client, rbac):

    other_user = rbac.create_basic_user(
        username = "arandomusertoupdate",
        email = "arandomemailtoupdate@example.com",
        password = "password"
    )

    endpoint = f"/v1/users/{other_user.id}"

    updated_data = {
        "username":"admin_updated_username"
    }

    response = admin_authenticated_client.put(endpoint, json = updated_data)

    assert response.status_code == status.HTTP_200_OK

def test_super_admin_can_update_user(super_admin_authenticated_client, test_user):

    endpoint = f"/v1/users/{test_user.id}"

    updated_data = {
        "username":"super_admin_updated_username"
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



def test_admin_can_delete_user(admin_authenticated_client, rbac):

    other_user = rbac.create_basic_user(
        username = "arandomusertodelete", 
        email = "arandomemailtodelete@example.com", 
        password = "password"
    )

    endpoint = f"/v1/users/{other_user.id}"

    response = admin_authenticated_client.delete(endpoint)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_super_admin_can_delete_user(super_admin_authenticated_client, test_delete_user):


    endpoint = f"/v1/users/{test_delete_user.id}"

    response = super_admin_authenticated_client.delete(endpoint)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_pagination_params(admin_authenticated_client):

    filtered_response = admin_authenticated_client.get("/v1/users?page=1&q=super")

    all_response = admin_authenticated_client.get("/v1/users")
    
    filtered_count = filtered_response.json()["count"]

    all_count = all_response.json()["count"]


    assert filtered_count != all_count










