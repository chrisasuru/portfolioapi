from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from ..models.user import UserRead, UserCreate, User
from ..db import engine, get_session
from ..core import utils
from sqlmodel import Session, select


users_router = APIRouter()


@users_router.get("/users", response_model = utils.PaginatedResponse)
async def list_users(session: Session = Depends(get_session)):

    statement = select(User)
    users = session.exec(statement).all()

    users = [UserRead.model_validate(user) for user in users]

    return utils.PaginatedResponse(
        results = users,
        count = len(users),
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