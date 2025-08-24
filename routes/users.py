from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi import status
from ..models.authentication.models import User, Role
from ..schemas.users import UserRead, UserCreate, UserUpdate
from ..database.setup import PROFILE
from ..database.db import engine, get_session
from ..database.crud.users import CRUDUser
from ..core import utils
from ..config import settings
from ..core.security import oauth2_scheme, PermissionChecker, get_current_user, get_permission_checker
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Annotated
import jwt

users_router = APIRouter()


crud_user = CRUDUser()



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

    access_token = jwt.encode(
        {"sub": str(user.id)},
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

    


@users_router.get("/users", response_model = utils.PaginatedResponse)
async def list_users(page: int = 1, current_user : User = Depends(get_current_user), session: Session = Depends(get_session), permission_checker: PermissionChecker = Depends(get_permission_checker)):
    

    
    resource_type = User.__tablename__
    has_perm = permission_checker.has_permissions(
        current_user, 
        'list', 
        resource_type
    )
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
async def create_user(user_data: UserCreate, session: Session = Depends(get_session)):

    user = crud_user.create(session, user_data)

    user = UserRead.model_validate(user)
        
    return user

@users_router.get("/users/{username}", response_model = UserRead)
async def get_user(username: str, session: Session = Depends(get_session)):

    user = crud_user.get(session, username = username)
    
    user = UserRead.model_validate(user)

    return user

@users_router.put("/users/{username}", response_model = UserRead)
async def update_user(username: str, user_data: UserUpdate, session: Session = Depends(get_session)):

    crud_user.update(session, user_data, username = None)

    user = UserRead.model_validate(user)

    return user

@users_router.delete("/users/{username}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(username: str, session: Session = Depends(get_session)):

    crud_user.delete(session, username = username)

    return None