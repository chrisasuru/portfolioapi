from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from sqlmodel import Field

M = TypeVar('M')

class PaginatedResponse(BaseModel, Generic[M]):
    next: Optional[str] = Field(
        default=None,
        description='URL to the next page of results, if available'
    )
    previous: Optional[str] = Field(
        default=None,
        description='URL to the previous page of results, if available'
    )
    count: int = Field(description='Number of items returned in the response')
    results: List[M] = Field(description='List of items returned in the response')