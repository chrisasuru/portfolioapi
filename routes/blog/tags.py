from fastapi import APIRouter, Depends
from fastapi import status
from sqlmodel import Session
from ...schemas.pagination import PaginatedResponse
from ...schemas.blog.tag import TagRead, TagCreate
from ...schemas.blog.post import BlogPostRead
from ...models.auth.permission import PermissionAction
from ...services.blog.blog_posts_service import BlogPostService
from ...core.rbac.dependencies import require_permission
from ...core.pagination.dependencies import get_query_parameters, get_pagination_params
from ...database.db import get_session
from ...models.root import BLOG_TAG_TABLE_NAME

blog_tag_router = APIRouter(prefix="/v1")

@blog_tag_router.get("/tags", status_code = status.HTTP_200_OK, response_model = PaginatedResponse)
def list_blog_tags(
    query_parameters: dict = Depends(get_query_parameters),
    pagination_params: str = Depends(get_pagination_params),
    session = Depends(get_session)):

    page_size = query_parameters["page_size"]
    page = query_parameters["page"]
    offset = (page - 1) * page_size

    blog_tags, count = BlogPostService.get_tags(
        session,
        q = query_parameters["q"],
        page = page,
        page_size = page_size,
        sort = query_parameters["sort"]
    )

    next_page = None if (offset + page_size) >= count else f"/v1/tags?page={page + 1}&{pagination_params}"
    previous_page = None if page == 1 else f"/v1/tags?page={page - 1}&{pagination_params}"


    return PaginatedResponse(
        results = blog_tags,
        count = count,
        next = None if (offset + page_size) >= count else next_page,
        previous = None if page == 1 else previous_page
    )
@blog_tag_router.post("/tags", status_code = status.HTTP_201_CREATED, response_model = TagRead)
def create_blog_tag(
    blog_tag_data: TagCreate, 
    session: Session = Depends(get_session), 
    has_permission: bool = Depends(require_permission(PermissionAction.CREATE, BLOG_TAG_TABLE_NAME))):

    blog_tag = BlogPostService.create_blog_tag(session, blog_tag_data)
    return blog_tag


@blog_tag_router.get("/tags/{blog_tag_slug}", status_code = status.HTTP_200_OK, response_model = TagRead)
def get_blog_tag(blog_tag_slug: str, session = Depends(get_session)):

    blog_tag = BlogPostService.get_blog_tag_by_slug(session, blog_tag_slug)

    return blog_tag

@blog_tag_router.get("/tags/{blog_tag_slug}", status_code = status.HTTP_200_OK, response_model = TagRead)
def update_blog_tag(blog_tag_slug: str, blog_tag_data: TagCreate, session = Depends(get_session)):

    blog_tag = BlogPostService.get_blog_tag_by_slug(session, blog_tag_slug)

    blog_tag = BlogPostService.update_blog_tag(session, blog_tag, blog_tag_data)

    return blog_tag

@blog_tag_router.delete("/tags/{blog_tag_slug}", status_code = status.HTTP_204_NO_CONTENT)
def delete_blog_tag(blog_tag_slug: str, 
                    session: Session = Depends(get_session),
                    has_bool: bool = Depends(require_permission(PermissionAction.DELETE, BLOG_TAG_TABLE_NAME))):

    blog_tag = BlogPostService.delete_blog_tag_by_slug(session, blog_tag_slug)

    return blog_tag

@blog_tag_router.get("/tags/{blog_tag_slug}/blog_posts", status_code = status.HTTP_200_OK, response_model = PaginatedResponse)
def list_blog_tag_blog_posts(
        blog_tag_slug: str, 
        query_parameters: dict = Depends(get_query_parameters),
        pagination_params: str = Depends(get_pagination_params),
        session = Depends(get_session)):
    
    page_size = query_parameters["page_size"]
    page = query_parameters["page"]
    offset = (page - 1) * page_size
    
    blog_posts, count = BlogPostService.get_blog_posts_by_tag_slug(
        session, 
        blog_tag_slug, 
        page = page, 
        page_size = page_size,
        sort = query_parameters["sort"]
    )

    blog_posts = [BlogPostRead.model_dump(blog_post) for blog_post in blog_posts]

    next_page = None if (offset + page_size) >= count else f"/v1/tags/{blog_tag_slug}/blog_posts?page={page + 1}&{pagination_params}"
    previous_page = None if page == 1 else f"/v1/tags/{blog_tag_slug}/blog_posts?page={page - 1}&{pagination_params}"


    return PaginatedResponse(
        results = blog_posts,
        count = count,
        next = None if (offset + page_size) >= count else next_page,
        previous = None if page == 1 else previous_page
    )
