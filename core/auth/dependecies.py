import jwt
from fastapi import Request, Depends
from ...models.auth.user import User
from sqlmodel import Session, select
from ...database.db import get_session
from ...config import settings

    

async def get_current_user(request: Request, session: Session = Depends(get_session)) -> User | None:

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