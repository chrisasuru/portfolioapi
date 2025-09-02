from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class AuthorDetail(BaseModel):

    username: str = Field(nullable = False)

class BlogCommentCreate(BaseModel):

    body: str = Field(nullable = False)

class BlogCommentReadWithRelatedFields(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(nullable = False)
    author: Optional[AuthorDetail] = None
    body: str = Field(nullable = False)
    created_at: datetime = Field(nullable = False)