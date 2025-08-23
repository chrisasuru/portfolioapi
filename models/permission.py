from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel


class RolePermissionLink(SQLModel, table = True):

    role_id: int = Field(default = None, foreign_key = "role.id", primary_key=True)
    permission_id: int = Field(default = None, foreign_key = "permission.id", primary_key = True)


class UserRoleLink(SQLModel, table = True):

    user_id: int = Field(default = None, foreign_key = "user.id", primary_key = True)
    role_id: int = Field(default = None, foreign_key = "role.id", primary_key = True)


class RoleBase(SQLModel):

    name: str = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False, default = "")

class PermissionBase(SQLModel):

    name: str = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False, default = "")
    resource: str = Field(nullable = False, default = "")
    action: str = Field(nullable = False, default = "")
    condition: str = Field(nullable = False, default = "always") # e.g., "always", "never", "owner", "group_member"




