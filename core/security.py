from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status
from ..config import settings
from ..db import get_session
from ..models.user import UserRead, User
from sqlalchemy import select
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session = Depends(get_session)):

    user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).get("sub")

    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid authentication credentials"
        )
    
    return user