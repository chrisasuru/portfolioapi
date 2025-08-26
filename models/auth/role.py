from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from .links import RolePermissionLink, UserRoleLink

class Role(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    name: str = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False, default = "")
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))
    permissions: list["Permission"] = Relationship(
        back_populates = "roles",
        link_model = RolePermissionLink
    )
    users: list["User"] = Relationship(
        back_populates = "roles",
        link_model = UserRoleLink
    )
