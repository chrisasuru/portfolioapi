
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from datetime import datetime, timezone
from typing import Optional
from .links import RolePermissionLink
from enum import Enum

class PermissionAction(str, Enum):

    LIST: str = 'list'
    CREATE: str = 'create'
    READ: str = 'read'
    UPDATE: str = 'update'
    DELETE: str = 'delete'
    ACTIVATE: str = 'activate'
    IMPERSONATE: str = 'impersonate'
    ASSIGN: str = 'assign'
    REVOKE: str = 'revoke'
    CREATE_DRAFT: str = 'create_draft'
    READ_DRAFT: str = 'read_draft'
    UPDATE_DRAFT: str = 'update_draft'
    DELETE_DRAFT: str = 'delete_draft'
    PUBLISH: str = 'publish'


class PermissionCondition(str, Enum):

    ALWAYS: str = 'always'
    OWNER: str = 'owner'
    SELF: str = 'self'
    SUPERIOR: str = 'superior'
    SELF_OR_SUPERIOR: str = 'self_or_superior'


class Permission(SQLModel, table = True):

    id: int | None = Field(default = None, primary_key = True)
    name: str = Field(index = True, unique = True, nullable = False)
    action: PermissionAction = Field(nullable = False, default = "")
    description: str = Field(nullable = False, default = "")
    condition: PermissionCondition = Field(nullable = False, default = None)
    resource: str = Field(nullable = False, default = "")
    created_at: Optional[datetime] = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))
    roles: list["Role"] = Relationship(
        back_populates = "permissions",
        link_model = RolePermissionLink
    )
    __table_args__ = (
        UniqueConstraint("action", "resource", "condition", ),
    )



