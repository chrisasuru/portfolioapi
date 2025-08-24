from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status
from ..config import settings
from ..database.db import get_session
from ..models.authentication.models import User, Role, Permission, ResourcePermission
from sqlalchemy import select
from sqlmodel import Session
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session = Depends(get_session)):

    user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).get("sub")

    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.scalars().first()

    if not user:

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid authentication credentials"
        )

    return user


class PermissionChecker:

    def __init__(self, session: Session):

        self.session = session
    
    def has_permission(self, user: User, action : str, resource_type: str, resource_id : int = None):
        # Filter based on roles and permissions
        return True
    
    def has_object_permission(self, user: User):

        return True



def get_permission_checker(session: Session = Depends(get_session)) -> PermissionChecker:

    return PermissionChecker(session)
