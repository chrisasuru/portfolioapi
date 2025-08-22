from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from ..models.user import UserRead, UserCreate, UserUpdate, User
from ..db import engine, get_session
from ..core import utils
from ..config import settings
from ..core.security import oauth2_scheme
from sqlmodel import Session, select
from sqlalchemy import func


users_router = APIRouter()


@users_router.get("/users", response_model = utils.PaginatedResponse)
async def list_users(page: int = 1, session: Session = Depends(get_session)):

    offset = (page - 1) * settings.DEFAULT_PAGE_SIZE

    count_statement = select(func.count(User.id))
    count = session.exec(count_statement).one()
    statement = select(User).offset(offset).limit(settings.DEFAULT_PAGE_SIZE)
    users = session.exec(statement).all()

    users = [UserRead.model_validate(user) for user in users]

    return utils.PaginatedResponse(
        results = users,
        count = count,
        next = None,
        previous = None
    )


@users_router.post("/users", status_code = status.HTTP_201_CREATED, response_model = UserRead)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    
    hashed_password = utils.hash_password(user.password)

    user_data = user.model_dump(exclude={"confirm_password", "password"})
    user_data["password"] = hashed_password

    user = User(**user_data)
        
    session.add(user)
    session.commit()
    session.refresh(user)

    user = UserRead.model_validate(user)
        
    return user

@users_router.get("/users/{username}", response_model = UserRead)
async def get_user(username: str, session: Session = Depends(get_session)):

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:

        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with username '{username}' not found."
        ) 
    
    user = UserRead.model_validate(user)

    return user

@users_router.put("/users/{username}", response_model = UserRead)
async def update_user(username: str, user_data: UserUpdate, session: Session = Depends(get_session)):

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:

        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with username '{username}' not found."
        )
    
    if user_data.password and user_data.confirm_password:

        user.password = utils.hash_password(user_data.password)

    user.username = user_data.username if user_data.username else user.username
    user.email = user_data.email if user_data.email else user.email
    user.first_name = user_data.first_name if user_data.first_name else user.first_name
    user.last_name = user_data.last_name if user_data.last_name else user.last_name

    session.add(user)
    session.commit()
    session.refresh(user)

    user = UserRead.model_validate(user)

    return user

@users_router.delete("/users/{username}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(username: str, session: Session = Depends(get_session)):

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:

        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with username '{username}' not found."
        )
    
    session.delete(user)
    session.commit()

    return None