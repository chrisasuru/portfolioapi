from pydantic import BaseModel, Field, ConfigDict
from ...models.blog.post import PublishingStatus
from .tag import TagRead
from typing import List, Optional

class AuthorDetail(BaseModel):

    first_name: str = Field(nullable = True)
    last_name: str = Field(nullable = True)

class BlogPostCreate(BaseModel):

    title: str = Field(nullable = False, max_length = 225, default = None)
    body: str = Field(nullable = False)
    tags: List[str] = []


class BlogPostRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(nullable = False)
    title: str = Field(nullable = False, max_length = 225, default = None)
    slug: str = Field(nullable = False)
    body: str = Field(nullable = False)
    publishing_status: PublishingStatus = Field(nullable = False)

class BlogPostReadWithRelatedFields(BaseModel):


    id: int = Field(nullable = False)
    author: Optional[AuthorDetail] = None
    slug: str = Field(nullable = False)
    title: str = Field(nullable = False)
    body: str = Field(nullable = False)
    tags: List[TagRead] = []

class BlogPostUpdate(BaseModel):

    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None

class BlogPostPublish(BaseModel):

    publishing_status: PublishingStatus = Field(nullable = False)