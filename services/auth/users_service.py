from sqlmodel import Session, select, SQLModel
from sqlalchemy import or_, and_, func
from ...schemas.auth.users import UserCreate, UserUpdate
from ...models.auth.user import User
from ...models.auth.role import Role
from ...core.auth.passwords import hash_password
from fastapi.exceptions import HTTPException
from fastapi import status
from ...config import settings
from typing import Optional
from enum import Enum


class UserService:


    @staticmethod
    def get_users(session: Session, q: str | None = None, page : int = 1, page_size : int = settings.DEFAULT_PAGE_SIZE, sort: str = "id"):

        if page < 1:

            page = page

        offset = (page - 1) * page_size

        if q:

            statement = select(User).where(or_(User.username.icontains(q), User.email.icontains(q)))
            count_statement = select(func.count(User.id)).where(or_(User.username.icontains(q), User.email.icontains(q)))

        else:

            statement = select(User)
            count_statement = select(func.count(User.id))

        sort_field = sort.replace("-", "") if sort else None

        order_by = getattr(User, sort_field, None) if sort_field else None
        
        if order_by:

            order_by = order_by.desc() if sort.startswith("-") else order_by

        statement = statement.order_by(order_by)
        
        statement = statement.offset(offset).limit(page_size)

        count = session.exec(count_statement).one()

        users = session.exec(statement).all()

        return users, count


    @staticmethod
    def get_user_by_id(session : Session, user_id: int) -> User:

        user = UserService._get_or_404(session, user_id)
        return user
    

    @staticmethod
    def create_user(session: Session, user_data: UserCreate) -> User:

        existing_user = session.exec(select(User).where(User.username == user_data.username)).one_or_none()

        if existing_user:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "The username field must be unique."
            )
        
        existing_user = session.exec(select(User).where(User.email == user_data.email)).one_or_none()

        if existing_user:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "The email field must be unique."
            )  
        
        
        user_data = user_data.model_dump()

        password = user_data.pop("password")
        confirm_password = user_data.pop("confirm_password")

        user_data["password"] = hash_password(password)

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
    def update_user(session: Session, user_id: int, user_data: UserUpdate) -> User:

        user = UserService._get_or_404(session, user_id)

        existing_user = session.exec(select(User).where(User.username == user_data.username)).one_or_none()

        if existing_user and existing_user != user:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "The username field must be unique."
            )  
        
        existing_user = session.exec(select(User).where(User.email == user_data.email)).one_or_none()

        if existing_user and existing_user != user:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "The email field must be unique."
            )  

        user_data = user_data.model_dump(exclude_unset = True, exclude = ['confirm_password'])
        password = user_data.pop("password", None)

        if password:

            user.password = hash_password(password)

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