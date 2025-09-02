from sqlmodel import SQLModel, Relationship, Field
from pydantic import EmailStr
from typing import Optional
from datetime import datetime, timezone
from .links import UserRoleLink
from fastapi import HTTPException, status

class User(SQLModel, table = True):


    id: int | None = Field(default = None, primary_key = True)
    username: str = Field(index = True, unique = True, nullable = False)
    email: EmailStr = Field(index = True, unique = True, nullable = False)
    first_name: Optional[str] = Field(nullable = True, default = None)
    last_name: Optional[str] = Field(nullable = True, default = None)
    date_joined: Optional[datetime] = Field(default_factory = lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default_factory = lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default = True)
    password : Optional[str] = Field(nullable = False, default = None)
    roles: list["Role"] = Relationship(
        back_populates = "users",
        link_model = UserRoleLink
    )
    blog_comments: list["BlogComment"] = Relationship(
        back_populates = "author"
    )
    blog_posts: list["BlogPost"] = Relationship(
        back_populates = "author"
    )

    def get_highest_rank(self):

        highest_rank = 0

        for role in self.roles:

            if role.rank > highest_rank:

                highest_rank = role.rank

        return highest_rank