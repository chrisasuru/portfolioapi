from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from .links import BlogPostBlogTagLink

class PublishingStatus(str, Enum):

    DRAFT: str = 'draft'
    REVIEW: str = 'review'
    PUBLISHED: str = 'published'


class BlogPost(SQLModel, table = True):

    id: Optional[int] = Field(default = None, primary_key = True)
    title: str = Field(nullable = False, max_length = 225, default = None)
    slug: Optional[str] = Field(nullable = False, unique = True)
    body: str = Field(nullable = True)
    publishing_status: PublishingStatus = Field(default = PublishingStatus.DRAFT)
    published_at: datetime = Field(nullable = True, default = None)
    last_edited: datetime = Field(nullable = True, default_factory = lambda: datetime.now(timezone.utc))
    author_id: int = Field(default = None, foreign_key = "user.id")
    author: Optional["User"] = Relationship(back_populates = "blog_posts")
    comments: List["BlogComment"] = Relationship(back_populates="blog_post")
    tags: List["BlogTag"] = Relationship(back_populates = "blog_posts", link_model = BlogPostBlogTagLink)