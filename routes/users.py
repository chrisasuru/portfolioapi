from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi import status
from ..models.auth.user import User
from ..services.auth.users_service import UserService
from ..schemas.users import UserRead, UserCreate, UserUpdate
from ..database.db import engine, get_session
from ..database.setup import OWNER
from ..core import utils
from ..config import settings
from ..core.security import generate_access_token, require_permission, get_current_user
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Annotated

users_router = APIRouter()


@users_router.post("/token")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()], session: Session = Depends(get_session)):

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user or not utils.check_password(password, user.password):

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid username or password"
        )
    
    user.last_login = datetime.now(timezone.utc)

    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = generate_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

    


@users_router.get("/users", response_model = utils.PaginatedResponse)
async def list_users(page: int = 1, 
                     session: Session = Depends(get_session), 
                     has_permission : bool = Depends(require_permission("user", "list"))):

    offset = (page - 1) * settings.DEFAULT_PAGE_SIZE

    count_statement = select(func.count(User.id))
    count = session.exec(count_statement).one()
    statement = select(User).offset(offset).limit(settings.DEFAULT_PAGE_SIZE)
    users = session.exec(statement).all()

    users = [UserRead.model_validate(user) for user in users]

    return utils.PaginatedResponse(
        results = users,
        count = count,
        next = None if offset + settings.DEFAULT_PAGE_SIZE >= count else f"/v1/users?page={page + 1}",
        previous = None if page <= 1 else f"/v1/users?page={page - 1}"
    )


@users_router.post("/users", status_code = status.HTTP_201_CREATED, response_model = UserRead)
async def create_user(user_data: UserCreate, 
                      session: Session = Depends(get_session),
                      has_permission : bool = Depends(require_permission("user", "create"))):
    
    
    created_user = UserService.create_user(session, user_data)

    created_user_schema = UserRead.model_validate(created_user)
        
    return created_user_schema

@users_router.get("/users/{user_id}", response_model = UserRead)
async def get_user(user_id: int, 
                   session: Session = Depends(get_session),
                   has_permission : bool = Depends(require_permission(
                          "user", "read", 
                          condition = OWNER, 
                          resource_param = "user_id"))):

    user = UserService.get_user_by_id(session, user_id)
    
    user_schema = UserRead.model_validate(user)

    return user_schema

@users_router.put("/users/{user_id}", response_model = UserRead)
async def update_user(user_id: int, 
                      user_data: UserUpdate, 
                      session: Session = Depends(get_session),
                      has_permission : bool = Depends(require_permission(
                          "user", "update", 
                          condition = OWNER, 
                          resource_param = "user_id"))):

    updated_user = UserService.update_user(session, user_id, user_data)

    updated_user_schema = UserRead.model_validate(updated_user)

    return updated_user_schema

@users_router.delete("/users/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, 
                      session: Session = Depends(get_session),
                      has_permission : bool = Depends(require_permission(
                          "user", "delete", 
                          condition = OWNER, 
                          resource_param = "user_id"))):

    user = UserService.delete_user(session, user_id)

    return user
