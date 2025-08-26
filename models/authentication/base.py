from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import UniqueConstraint
from pydantic import EmailStr

class UserBase(SQLModel):

    username: str = Field(index = True, unique = True, nullable = False)
    email: EmailStr = Field(index = True, unique = True, nullable = False)
    first_name: Optional[str] = Field(nullable = True, default = None)
    last_name: Optional[str] = Field(nullable = True, default = None)


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
    condition: str = Field(nullable = False, default = None)
    resource: str = Field(nullable = False, default = "")
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("action", "resource", "condition", ),
    )


