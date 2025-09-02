from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone

class BlogComment(SQLModel, table = True):

    id: Optional[int] = Field(default = None, primary_key = True)
    body: str = Field(nullable = False, max_length = 300)
    created_at: datetime = Field(nullable = False, default_factory = lambda: datetime.now(timezone.utc))
    author_id: int = Field(foreign_key = "user.id")
    author: Optional["User"] = Relationship(back_populates = "blog_comments")
    blog_post_id: int = Field(foreign_key = "blogpost.id")
    blog_post: Optional["BlogPost"] = Relationship(back_populates = "comments")
