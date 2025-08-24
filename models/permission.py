from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import UniqueConstraint

class RolePermissionLink(SQLModel, table = True):

    role_id: int = Field(default = None, foreign_key = "role.id", primary_key=True)
    permission_id: int = Field(default = None, foreign_key = "permission.id", primary_key = True)


class UserRoleLink(SQLModel, table = True):

    user_id: int = Field(default = None, foreign_key = "user.id", primary_key = True)
    role_id: int = Field(default = None, foreign_key = "role.id", primary_key = True)


class RoleBase(SQLModel):

    name: str = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False, default = "")
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))

class PermissionBase(SQLModel):

    name: str = Field(index = True, unique = True, nullable = False)
    action: str = Field(nullable = False, default = "")
    description: str = Field(nullable = False, default = "")
    resource: str = Field(nullable = False, default = "")
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("action", "resource", ),
    )

class ResourcePermissionBase(SQLModel):

    user_id: int = Field(default = None, foreign_key = "user.id")
    permission_id: int = Field(default = None, foreign_key = "permission.id")
    resource_type: str = Field(default = None, max_length = 50)
    resource_id: int = Field(nullable = True, default = None)
    name: str = Field(nullable = False, default = "")
    action: str = Field(nullable = False, default = "")
    description:str = Field(nullable = False, default = "")
    granted_by: int = Field(default = None, foreign_key = "user.id")
    granted_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.now))

    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", "action", "resource_type", "resource_id"),
    )