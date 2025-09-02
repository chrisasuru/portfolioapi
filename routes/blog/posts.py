from fastapi import APIRouter, Depends
from fastapi import status
from sqlmodel import Session
from ...schemas.blog.post import BlogPostCreate, BlogPostReadWithRelatedFields, BlogPostRead, BlogPostUpdate, BlogPostPublish
from ...schemas.blog.comment import BlogCommentCreate, BlogCommentReadWithRelatedFields
from ...core.pagination.dependencies import get_query_parameters, get_pagination_params
from ...core.rbac.dependencies import require_permission, get_current_user
from ...schemas.pagination import PaginatedResponse
from ...models.auth.permission import PermissionAction
from ...services.blog.blog_posts_service import BlogPostService
from ...models.blog.post import BlogPost
from ...models.blog.comment import BlogComment
from ...models.auth.user import User
from ...models.root import BLOG_POST_TABLE_NAME, BLOG_COMMENT_TABLE_NAME
from ...database.db import get_session

blog_post_router = APIRouter(prefix="/v1")



@blog_post_router.get("/blog_posts", status_code = status.HTTP_200_OK, response_model = PaginatedResponse)
async def list_blog_posts(
    query_parameters: dict = Depends(get_query_parameters),
    pagination_params: str = Depends(get_pagination_params),
    session = Depends(get_session)):

    page = query_parameters["page"]
    page_size = query_parameters["page_size"]
    offset = (page - 1) * page_size

    blog_posts, count = BlogPostService.get_blog_posts(
        session,
        q  = query_parameters["q"],
        page = page,
        page_size = page_size,
        sort = query_parameters["sort"]
    )

    next_page = None if (offset + page_size) >= count else f"/v1/blog_tags?page={page + 1}&{pagination_params}"
    previous_page = None if page == 1 else f"/v1/blog_posts?page={page - 1}&{pagination_params}"

    
    return PaginatedResponse(
        results = blog_posts,
        count = count,
        next = None if (offset + page_size) >= count else next_page,
        previous = None if page == 1 else previous_page
    )

@blog_post_router.post("/blog_posts", status_code = status.HTTP_201_CREATED, response_model = BlogPostRead)
async def create_blog_post(blog_post_data: BlogPostCreate, 
                           session: Session = Depends(get_session),
                           current_user: User = Depends(get_current_user),
                           has_permission: bool = Depends(require_permission(PermissionAction.CREATE, BLOG_POST_TABLE_NAME))):
    
    created_blog_post = BlogPostService.create_blog_post(session, blog_post_data, current_user)

    return created_blog_post

@blog_post_router.get("/blog_posts/{blog_post_id}", status_code = status.HTTP_200_OK, response_model = BlogPostReadWithRelatedFields)
async def read_blog_post(blog_post_id: int,
                         session: Session = Depends(get_session),
                         has_permission: bool = Depends(require_permission(PermissionAction.READ_DRAFT, BLOG_POST_TABLE_NAME, lookup_field = "blog_post_id"))):
    
    blog_post = BlogPostService.get_blog_post_by_id(session, blog_post_id)

    return blog_post

@blog_post_router.put("/blog_posts/{blog_post_id}", status_code = status.HTTP_200_OK)
async def update_blog_post(blog_post_id: int,
                           blog_post_data: BlogPostUpdate,
                           session: Session = Depends(get_session),
                           has_permission: bool = Depends(require_permission(PermissionAction.UPDATE, BLOG_POST_TABLE_NAME))):
    
    blog_post = BlogPostService.get_blog_post_by_id(session, blog_post_id)

    updated_blog_post = BlogPostService.update_blog_post(session, blog_post, blog_post_data)

    return updated_blog_post

@blog_post_router.put("/blog_posts/{blog_post_id}/publish", status_code = status.HTTP_200_OK, response_model = BlogPostRead)
async def publish_blog_post(blog_post_id: int, 
                            blog_post_data: BlogPostPublish,
                            session: Session = Depends(get_session),
                            has_permission: bool = Depends(require_permission(PermissionAction.PUBLISH, BLOG_POST_TABLE_NAME))):
    
    blog_post = BlogPostService.get_blog_post_by_id(session, blog_post_id)
    
    blog_post = BlogPostService.update_blog_post(session, blog_post, blog_post_data)

    return blog_post


@blog_post_router.delete("/blog_posts/{blog_post_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_blog_post(blog_post_id: int,
                           session: Session = Depends(get_session), 
                           has_permission: bool = Depends(require_permission(PermissionAction.DELETE, BLOG_POST_TABLE_NAME))):

    blog_post = BlogPostService.get_blog_post_by_id(session, blog_post_id)

    BlogPostService.delete_blog_post(session, blog_post)

    return None


@blog_post_router.get("/blog_posts/{blog_post_id}/comments", status_code = status.HTTP_200_OK, response_model = PaginatedResponse)
async def get_blog_post_comments(blog_post_id: int, 
                                 query_parameters: dict = Depends(get_query_parameters),
                                 pagination_params: str = Depends(get_pagination_params),
                                 current_user: User = Depends(get_current_user),
                                 session: Session = Depends(get_session)):
    

    page = query_parameters["page"]
    page_size = query_parameters["page_size"]
    offset = (page - 1) * page_size
    
    comments, count = BlogPostService.get_blog_post_comments(
        session, 
        blog_post_id,
        q  = query_parameters["q"],
        page = page,
        page_size = page_size,
        sort = query_parameters["sort"]
    )

    next_page = None if (offset + page_size) >= count else f"/v1/blog_tags/{blog_post_id}/comments?page={page + 1}&{pagination_params}"
    previous_page = None if page == 1 else f"/v1/blog_posts/{blog_post_id}/comments?page={page - 1}&{pagination_params}"

    
    return PaginatedResponse(
        results = comments,
        count = count,
        next = None if (offset + page_size) >= count else next_page,
        previous = None if page == 1 else previous_page
    )


@blog_post_router.post("/blog_posts/{blog_post_id}/comments", status_code = status.HTTP_201_CREATED, response_model = BlogCommentReadWithRelatedFields)
async def create_blog_post_comment(
                                blog_post_id: int,
                                blog_comment_data: BlogCommentCreate,
                                current_user: User = Depends(get_current_user),
                                session: Session = Depends(get_session),
                                has_permission: bool = Depends(require_permission(PermissionAction.CREATE, BLOG_COMMENT_TABLE_NAME))):
    

    blog_post_comment = BlogPostService.create_blog_post_comment(session, blog_post_id, current_user.id, blog_comment_data)

    response_data = {
        "author":{
            "username": blog_post_comment.author.username
        },
        "id": blog_post_comment.id,
        "body": blog_post_comment.body,
        "created_at": blog_post_comment.created_at

    }

    return response_data
    

@blog_post_router.delete("/blog_posts/{blog_post_id}/comments/{blog_comment_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_blog_post_comment(
                                blog_post_id: int,
                                blog_comment_id: int,
                                session: Session = Depends(get_session),
                                has_permission: bool = Depends(require_permission(PermissionAction.DELETE, BLOG_COMMENT_TABLE_NAME, lookup_field = "blog_comment_id"))):
    
    deleted_blog_comment = BlogPostService.delete_blog_post_comment(session, blog_comment_id)

    return deleted_blog_comment