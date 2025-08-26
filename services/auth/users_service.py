from sqlmodel import Session, select
from ...schemas.users import UserCreate, UserUpdate
from ...models.auth.user import User
from ...models.auth.role import Role
from ...core import utils
from fastapi.exceptions import HTTPException
from fastapi import status
from ...config import settings

class UserService:

    @staticmethod
    def get_user_by_id(session : Session, user_id: int) -> User:

        user = UserService._get_or_404(session, user_id)
        return user
    

    @staticmethod
    def create_user(session: Session, create_schema: UserCreate) -> User:

        user_data = create_schema.model_dump()

        password = user_data.pop("password")
        confirm_password = user_data.pop("confirm_password")

        user_data["password"] = utils.hash_password(password)

        user = User(**user_data)

        default_user_role_query = select(Role).where(Role.name == settings.DEFAULT_USER_ROLE)
        role = session.exec(default_user_role_query).one_or_none()

        if not role:

            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Default role '{settings.DEFAULT_USER_ROLE}' not found."
            )
        
        user.roles.append(role)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user
    
  
    @staticmethod
    def update_user(session: Session, user_id: int, update_schema: UserUpdate) -> User:

        user = UserService._get_or_404(session, user_id)
        user_data = update_schema.model_dump(exclude_unset = True, exclude = ['confirm_password'])
        password = user_data.pop("password", None)

        if password:

            user.password = utils.hash_password(password)

        for field, value in user_data.items():

            setattr(user, field, value)
            
        session.add(user)
        session.commit()
        session.refresh(user)

        return user
    

    @staticmethod
    def delete_user(session: Session, user_id: int) -> None:

        user = UserService._get_or_404(session, user_id)

        session.delete(user)
        session.commit()

        return None
    
    @staticmethod
    def _get_or_404(session: Session, user_id: int):

        user = session.get(User, user_id)

        if not user:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"User with id {user_id} not found."
            )
        return user

