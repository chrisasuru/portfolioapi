from pydantic import BaseModel, EmailStr, field_validator, model_validator, ConfigDict, Field
from typing import Optional
from ...config import settings
from datetime import datetime


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



class UserCreate(BaseModel):

    username: str = Field(nullable = False, default = None)
    email: EmailStr = Field(nullable = False, default = None)
    first_name: Optional[str] = Field(nullable = True, default = None)
    last_name: Optional[str] = Field(nullable = True, default = None)
    password: str = Field(nullable = False, min_length = 8, max_length = 128)
    confirm_password: str = Field(nullable = False, min_length = 8, max_length = 128)

    @field_validator("username")
    def validate_username(cls, value: str):

        if value in settings.RESERVED_USERNAMES:

            raise ValueError(f"Username '{value}' is reserved and cannot be used.")
            
        return value

        
    @model_validator(mode = "after")
    def check_passwords_match(self):

        if self.password != self.confirm_password:

            raise ValueError("Passwords do not match.")
        
        return self


class UserUpdate(BaseModel):

    username: Optional[str] = Field(nullable = True, default = None)
    email: Optional[EmailStr] = Field(nullable = True, default = None)
    first_name: Optional[str] = Field(nullable = True, default = None)
    last_name: Optional[str] = Field(nullable = True, default = None)
    password: Optional[str] = Field(nullable = True, min_length = 8, max_length = 128, default = None)
    confirm_password: Optional[str] = Field(nullable = True, min_length = 8, max_length = 128, default = None)

    @model_validator(mode = "after")
    def check_passwords_match(self):

        if self.password and self.password != self.confirm_password:

            raise ValueError("Passwords do not match.")
        
        return self
