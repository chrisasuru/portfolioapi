from fastapi import APIRouter, Depends
from fastapi import status
from ..models.auth.user import User
from ..services.auth.users_service import UserService
from ..schemas.auth.users import UserRead, UserCreate, UserUpdate
from ..database.db import get_session
from ..models.auth.permission import PermissionCondition, PermissionAction
from ..models.root import USER_TABLE_NAME
from ..schemas.pagination import PaginatedResponse
from ..core.pagination.dependencies import get_query_parameters, get_pagination_params
from ..config import settings
from ..core.rbac.dependencies import require_permission
from sqlmodel import Session


user_router = APIRouter(prefix="/v1")


@user_router.get("/users", response_model = PaginatedResponse)
async def list_users(query_parameters: dict = Depends(get_query_parameters),
                     pagination_params: str = Depends(get_pagination_params),
                     session: Session = Depends(get_session),
                     has_permission: bool = Depends(require_permission(PermissionAction.LIST, USER_TABLE_NAME))):
    
    
    page = query_parameters["page"]
    page_size = query_parameters["page_size"]
    offset = (page - 1) * page_size

    users, count = UserService.get_users(
        session, 
        q = query_parameters["q"],
        page = page,
        page_size = page_size,
        sort = query_parameters["sort"]
    )

    users = [UserRead.model_validate(user) for user in users]

    next_page = None if (offset + page_size) >= count else f"/v1/users?page={page + 1}&{pagination_params}"
    previous_page = None if page == 1 else f"/v1/users?page={page - 1}&{pagination_params}"


    return PaginatedResponse(
        results = users,
        count = count,
        next = None if (offset + page_size) >= count else next_page,
        previous = None if page == 1 else previous_page,
    )



@user_router.post("/users", status_code = status.HTTP_201_CREATED, response_model = UserRead)
async def create_user(user_data: UserCreate, 
                      session: Session = Depends(get_session),
                      has_permission : bool = Depends(require_permission(PermissionAction.CREATE, USER_TABLE_NAME))):
    
    
    created_user = UserService.create_user(session, user_data)

    created_user_schema = UserRead.model_validate(created_user)
        
    return created_user_schema

@user_router.get("/users/{user_id}", response_model = UserRead)
async def get_user(user_id: int, 
                   session: Session = Depends(get_session),
                   has_permission : bool = Depends(require_permission(
                          PermissionAction.READ, USER_TABLE_NAME, lookup_field = "user_id"))):
    

    user = UserService.get_user_by_id(session, user_id)
    
    user_schema = UserRead.model_validate(user)

    return user_schema

@user_router.put("/users/{user_id}", response_model = UserRead)
async def update_user(user_id: int, 
                      user_data: UserUpdate, 
                      session: Session = Depends(get_session),
                      has_permission : bool = Depends(require_permission(
                          PermissionAction.UPDATE, USER_TABLE_NAME, lookup_field = "user_id"))):

    updated_user = UserService.update_user(session, user_id, user_data)

    updated_user_schema = UserRead.model_validate(updated_user)

    return updated_user_schema

@user_router.delete("/users/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, 
                      session: Session = Depends(get_session),
                      has_permission : bool = Depends(require_permission(
                          PermissionAction.DELETE, USER_TABLE_NAME, lookup_field = "user_id"))):

    user = UserService.delete_user(session, user_id)

    return user
