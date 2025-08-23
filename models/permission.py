from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class RoleBase(SQLModel):

    name: str = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False, default = "")

class PermissionBase(SQLModel):

    name: str = Field(index = True, unique = True, nullable = False)
    description: str = Field(nullable = False, default = "")