from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from pydantic import ConfigDict
from datetime import datetime, timezone
from typing import Optional
from .permission import RoleBase, UserRoleLink, PermissionBase, RolePermissionLink

RESERVED_USERNAMES = {"admin", "user", "test", "root"}


class UserBase(SQLModel):

    username: str = Field(index = True, unique = True, nullable = False)
    email: EmailStr = Field(index = True, unique = True, nullable = False)
    first_name: Optional[str] = Field(nullable = True, default = None)
    last_name: Optional[str] = Field(nullable = True, default = None)


class User(UserBase, table = True):

    id: int | None = Field(default = None, primary_key = True)
    date_joined: Optional[datetime] = Field(default_factory = lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default_factory = lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default = True)
    is_superuser: bool = Field(default = False)
    is_staff: bool = Field(default = False)
    password : Optional[str] = Field(nullable = False, default = None)
    roles: list["Role"] = Relationship(
        back_populates = "users",
        link_model = UserRoleLink
    )


class UserRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_joined: datetime
    last_login: datetime
    is_active: bool


class UserCreate(UserBase):

    password: str = Field(nullable = False, min_length = 8, max_length = 128)
    confirm_password: str = Field(nullable = False, min_length = 8, max_length = 128)

    @field_validator("username")
    def validate_username(cls, value: str):

        if value in RESERVED_USERNAMES:

            raise ValueError(f"Username '{value}' is reserved and cannot be used.")
            
        return value

        
    @model_validator(mode = "after")
    def check_passwords_match(self):

        if self.password != self.confirm_password:

            raise ValueError("Passwords do not match.")
        
        return self


class UserUpdate(UserBase):

    username: Optional[str] = Field(nullable = True, default = None)
    email: Optional[EmailStr] = Field(nullable = True, default = None)
    password: Optional[str] = Field(nullable = True, min_length = 8, max_length = 128, default = None)
    confirm_password: Optional[str] = Field(nullable = True, min_length = 8, max_length = 128, default = None)

    @model_validator(mode = "after")
    def check_passwords_match(self):

        if self.password and self.password != self.confirm_password:

            raise ValueError("Passwords do not match.")
        
        return self


class Role(RoleBase, table = True):

    id: int | None = Field(default = None, primary_key = True)
    permissions: list["Permission"] = Relationship(
        back_populates = "roles",
        link_model = RolePermissionLink
    )
    users: list[User] = Relationship(
        back_populates = "roles",
        link_model = UserRoleLink
    )

class Permission(PermissionBase, table = True):

    id: int | None = Field(default = None, primary_key = True)
    roles: list["Role"] = Relationship(
        back_populates = "permissions",
        link_model = RolePermissionLink
    )
