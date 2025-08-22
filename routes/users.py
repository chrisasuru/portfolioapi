from fastapi import APIRouter, Depends, HTTPException
from ..models.user import UserRead, UserCreate, User
from ..db import engine
from ..core import utils
from sqlmodel import Session

users_router = APIRouter()


@users_router.post("/users")
async def create_user(user_create: UserCreate):
    
    hashed_password = utils.hash_password(user_create.password)

    user_data = user_create.model_dump(exclude={"confirm_password", "password"})
    user_data["password"] = hashed_password

    user = User(**user_data)

    with Session(engine) as session:
        
        session.add(user)
        session.commit()
        session.refresh(user)

        user_data["id"] = user.id
        
        return UserRead(**user_data)


