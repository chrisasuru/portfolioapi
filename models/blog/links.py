from sqlmodel import SQLModel, Field


class BlogPostBlogTagLink(SQLModel, table = True):

    post_id: int = Field(foreign_key = "blogpost.id", primary_key = True)
    tag_id: int = Field(foreign_key = "blogtag.id", primary_key = True)
