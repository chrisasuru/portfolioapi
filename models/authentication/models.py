from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import Optional
from .base import RoleBase, PermissionBase, RolePermissionLink, UserBase, UserRoleLink

class User(UserBase, table = True):


    id: int | None = Field(default = None, primary_key = True)
    date_joined: Optional[datetime] = Field(default_factory = lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default_factory = lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default = True)
    password : Optional[str] = Field(nullable = False, default = None)
    roles: list["Role"] = Relationship(
        back_populates = "users",
        link_model = UserRoleLink
    )


class Role(RoleBase, table = True):


    id: int | None = Field(default = None, primary_key = True)

    permissions: list["Permission"] = Relationship(
        back_populates = "roles",
        link_model = RolePermissionLink
    )
    users: list["User"] = Relationship(
        back_populates = "roles",
        link_model = UserRoleLink
    )



class Permission(PermissionBase, table = True):

    id: int | None = Field(default = None, primary_key = True)
    roles: list["Role"] = Relationship(
        back_populates = "permissions",
        link_model = RolePermissionLink
    )