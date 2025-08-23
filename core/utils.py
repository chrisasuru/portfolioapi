import bcrypt
from ..config import settings
from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, Generic, TypeVar, List
from sqlmodel import Field
M = TypeVar('M')


def hash_password(password: str) -> str:

    password = password.encode('utf-8')

    hashed_password = bcrypt.hashpw(
        password, 
        bcrypt.gensalt(15)
    )

    hashed_password = hashed_password.decode('utf-8')

    return hashed_password

def check_password(password: str, hashed_password: str) -> bool:

    password = password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password, hashed_password)


class AuthToken(BaseModel):

    token: str = Field(
        default = None,
        description='JWT token for user authentication'
    )


class PaginatedResponse(BaseModel):


    next: Optional[str] = Field(
        default = None,
        description = 'URL to the next page of results, if available'
    )
    previous: Optional[str] = Field(
        default = None,
        description = 'URL to the previous page of results, if available'
    )
    count: int = Field(description='Number of items returned in the response')
    results: List[M] = Field(description='List of items returned in the response following given criteria')