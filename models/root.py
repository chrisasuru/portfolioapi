from .auth.permission import Permission
from .auth.role import Role
from .auth.user import User
from .blog.comment import BlogComment
from .blog.post import BlogPost
from .blog.tag import BlogTag


USER_TABLE_NAME = User.__tablename__
ROLE_TABLE_NAME = Role.__tablename__
PERMISSION_TABLE_NAME = Permission.__tablename__
BLOG_COMMENT_TABLE_NAME = BlogComment.__tablename__
BLOG_POST_TABLE_NAME = BlogPost.__tablename__
BLOG_TAG_TABLE_NAME = BlogTag.__tablename__
