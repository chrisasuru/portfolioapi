from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from .links import BlogPostBlogTagLink

class BlogTag(SQLModel, table = True):

    id: Optional[int] = Field(default = None, primary_key = True)
    name: str = Field(nullable = False, unique = True, default = None)
    slug: str = Field(nullable = False, unique = True, default = None)
    blog_posts: List["BlogPost"] = Relationship(back_populates = "tags", link_model = BlogPostBlogTagLink)
