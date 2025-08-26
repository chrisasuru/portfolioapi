from sqlmodel import Session, select
from ..schemas.users import UserCreate, UserUpdate
from ..models.authentication.models import User, Role
from ..core import utils
from fastapi.exceptions import HTTPException
from fastapi import status
from ..config import settings

class UserFactory:

    def __init__(self, session: Session):

        self.session = session

    def get_user_by_id(self, user_id: int) -> User:

        user = self.session.get(User, user_id)

        if not user:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"User with id {user_id} not found."
            )

        return user

    def create_user(self, create_schema: UserCreate) -> User:

        user_data = create_schema.model_dump()

        password = user_data.pop("password")
        confirm_password = user_data.pop("confirm_password")

        user_data["password"] = utils.hash_password(password)

        user = User(**user_data)

        default_user_role_query = select(Role).where(Role.name == settings.DEFAULT_USER_ROLE)
        role = self.session.exec(default_user_role_query).one_or_none()

        if not role:

            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Default role '{settings.DEFAULT_USER_ROLE}' not found."
            )
        
        user.roles.append(role)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user
        
    def update_user(self, user_id: int, update_schema: UserUpdate) -> User:

        user = self.session.get(User, user_id)

        if not user:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"User with id {user_id} not found."
            )
        
        user_data = update_schema.model_dump(exclude_unset = True, exclude = ['confirm_password'])
        password = user_data.pop("password", None)

        if password:

            user.password = utils.hash_password(password)

        for field, value in user_data.items():

            setattr(user, field, value)
            
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user
    
    def delete_user(self, user_id: int) -> None:

        user = self.session.get(User, user_id)

        if not user:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"User with id {user_id} not found."
            )
        
        self.session.delete(user)
        self.session.commit()

        return None