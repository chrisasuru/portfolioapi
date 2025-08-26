
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from datetime import datetime, timezone
from typing import Optional
from .links import RolePermissionLink

class Permission(SQLModel, table = True):

    id: int | None = Field(default = None, primary_key = True)
    name: str = Field(index = True, unique = True, nullable = False)
    action: str = Field(nullable = False, default = "")
    description: str = Field(nullable = False, default = "")
    condition: str = Field(nullable = False, default = None)
    resource: str = Field(nullable = False, default = "")
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))
    roles: list["Role"] = Relationship(
        back_populates = "permissions",
        link_model = RolePermissionLink
    )
    __table_args__ = (
        UniqueConstraint("action", "resource", "condition", ),
    )



