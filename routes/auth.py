from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi import status
from typing import Annotated
from sqlmodel import Session, select
from ..models.auth.user import User
from datetime import datetime, timezone
from ..core.auth.tokens import generate_access_token
from ..core.auth.passwords import check_password
from ..database.db import get_session
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")



auth_router = APIRouter(prefix="/v1/auth")

@auth_router.post("/token")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()], session: Session = Depends(get_session)):

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user or not check_password(password, user.password):

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid username or password"
        )
    
    user.last_login = datetime.now(timezone.utc)

    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = generate_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }