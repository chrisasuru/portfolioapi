from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from ..config import settings
from ..database.db import get_session
from ..models.authentication.models import User, Role, Permission
from sqlmodel import SQLModel
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select, and_
from typing import Optional
import jwt

CREATE = "create"
READ = "read"
UPDATE = "update"
DELETE = "delete"
LIST = "list"

USER = "user"
ROLE = "role"
PERMISSION = "permission"

RESOURCE_NAME_TO_MODEL_MAPPING = {
    USER: User,
    ROLE: Role,
    PERMISSION: Permission
}


ALWAYS = "always"
OWNER = "owner"

def get_model_by_table_name(table_name):

    return RESOURCE_NAME_TO_MODEL_MAPPING[table_name]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")



async def get_authenticated_user(request: Request, session: Session = Depends(get_session)) -> User | None:

    headers = request.headers
    authorization = headers.get("authorization")

    if not authorization:

        return None
    
    bearer, token = authorization.split(" ")

    if bearer.lower() != "bearer":

        return None
    

    try:

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if not user_id:

            return None
    
    except jwt.exceptions.ExpiredSignatureError:

        return None
    
    except jwt.exceptions.PyJWTError:

        return None
    
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.scalars().first()

    if not user:

        return None
    
    return user


def generate_access_token(user_id: str | int):

    user_id = str(user_id)
    expires = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": user_id, "exp": expires},
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return access_token


def check_condition(user: User, item: SQLModel, condition : str = ALWAYS):
    
    if condition == OWNER:

        if item.__tablename__ == user.__tablename__:

            return user.id == item.id
        
        return item.user_id == user.id
    
    return condition == ALWAYS




def require_permission(
        resource: str, 
        action: str, 
        condition: Optional[str] = None,
        resource_param: Optional[str] = None):
    
    async def permission_checker(
            request: Request, 
            current_user: User | None = Depends(get_authenticated_user),
            session: Session = Depends(get_session)):
        

        if action == CREATE and USER == resource and not current_user:

            return True
        
        item = None


        permission_conditions = [Permission.resource == resource, Permission.action == action]

        if condition:

            permission_conditions.append(Permission.condition == condition)

        resource_id = None

        if resource_param:

            resource_id = request.path_params.get(resource_param)
            model = get_model_by_table_name(resource)
            item = session.get(model, resource_id)

        combined_conditions = and_(*permission_conditions)

        permission = session.exec(select(Permission).where(combined_conditions)).first()
        print(permission)

        if not permission:

            raise HTTPException(
                status = status.HTTP_403_FORBIDDEN,
                detail = f"The {action} {resource} {resource_id} permission with the condition {condition} does not exist."
            )
        
        user_permission_ids = []

        for role in current_user.roles:

            for permission in role.permissions:

                user_permission_ids.append(permission.id)

        has_permission = len(set([permission.id, ]).intersection(set(user_permission_ids))) > 0

        if has_permission:

            return check_condition(current_user, item, condition = condition)
        
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action."
        )
    
    return permission_checker




