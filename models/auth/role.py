from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from .links import RolePermissionLink, UserRoleLink
from enum import Enum

class RoleName(str, Enum):

    USER: str = 'user'
    VIEWER: str = 'viewer'
    PUBLISHER: str = 'publisher'
    EDITOR: str = 'editor'
    ADMIN: str = 'admin'
    SUPER_ADMIN: str = 'super_admin'

class RoleRank(int, Enum):
    USER: int = 1
    VIEWER: int = 2
    PUBLISHER: int = 2
    EDITOR: int = 2
    ADMIN: int = 3
    SUPER_ADMIN: int = 4


class Role(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    name: RoleName = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False)
    rank: RoleRank = Field(nullable = False)
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))
    permissions: list["Permission"] = Relationship(
        back_populates = "roles",
        link_model = RolePermissionLink
    )
    users: list["User"] = Relationship(
        back_populates = "roles",
        link_model = UserRoleLink
    )
