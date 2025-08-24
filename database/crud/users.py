from sqlmodel import Session, select
from ...schemas.users import UserCreate, UserUpdate, UserRead
from ...models.authentication.models import User, Role
from ...core import utils
from ...config import settings
from fastapi import HTTPException, status


class CRUDUser:


    def get(self, session: Session, user_id: int | str = None, username : str = None):

        if user_id:

            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).scalars().one()
        
        else:

            statement = select(User).where(User.username == username)
            user = session.exec(statement).scalars().one()

        if not user:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"User with id {user_id} not found."
            )
        
        return user
    
    def create(self, session: Session, user_data: UserCreate):

        password = user_data.pop("password")
        user_data.pop("confirm_password")

        user_data["password"] = utils.hash_password(password)

        user = User(**user_data)
        role = session.exec(select(Role).where(Role.name == settings.DEFAULT_ROLE)).first()
    
        user.roles.append(role)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user
    

    def update(self, session: Session, user_data: UserUpdate, user_id: int | str = None, username: str = None):

        user = self.get(session, user_id = user_id, username = username)
        password = user_data.pop("password")
        user_data.pop("confirm_password")

        for field, value in user_data.items():

            setattr(user, field, value)

        if password:

            user.password = utils.hash_password(password)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user
    
    def delete(self, session: Session, user_id: int | str = None, username: str = None):

        user = self.get(session, user_id = user_id, username = username)
        session.delete(user)
        session.commit()

        return None
