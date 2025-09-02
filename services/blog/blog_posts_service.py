from sqlmodel import Session, select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from ...models.blog.post import BlogPost, PublishingStatus
from ...models.blog.tag import BlogTag
from ...models.blog.comment import BlogComment
from ...models.auth.user import User
from ...schemas.blog.post import BlogPostCreate, BlogPostUpdate, BlogPostPublish
from ...schemas.blog.comment import BlogCommentCreate
from ...schemas.blog.tag import TagCreate
from ...config import settings
from slugify import slugify
from datetime import datetime, timezone


class BlogPostService:



    @staticmethod
    def create_blog_post(session: Session, blog_post_data: BlogPostCreate, current_user: User):

        slug = slugify(blog_post_data.title.lower())


        existing_blog_post = session.exec(select(BlogPost).where(BlogPost.slug == slug)).one_or_none()

        if existing_blog_post:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"A blog post with slug {slug} already exists."
            )
        
        blog_post_data = blog_post_data.model_dump()
        tags = blog_post_data.pop("tags", [])
        blog_post_data["slug"] = slug
        

        blog_post = BlogPost(**blog_post_data)
        blog_post.author_id = current_user.id

        for tag_name in tags:

            tag_name = tag_name.lower().strip()
            tag_slug = slugify(tag_name)

            existing_tag = session.exec(select(BlogTag).where(BlogTag.slug == tag_slug)).one_or_none()

            if existing_tag:

                blog_post.tags.append(existing_tag)

            else:

                created_tag = BlogTag(name = tag_name, slug = tag_slug)
                session.add(created_tag)
                session.commit()
                session.refresh(created_tag)
                blog_post.tags.append(created_tag)


        session.add(blog_post)
        session.commit()
        session.refresh(blog_post)
        
        return blog_post
    
    @staticmethod
    def create_blog_tag(session: Session, blog_tag_data: TagCreate):

        blog_tag_data = blog_tag_data.model_dump()
        name = blog_tag_data["name"].lower().strip()
        slug = slugify(name)

        existing_tag = session.exec(select(BlogTag).where(BlogTag.slug == slug)).first()

        if existing_tag:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Blog tag slug must be unique."
            )
        
        blog_tag = BlogTag(name = name, slug = slug)

        session.add(blog_tag)
        session.commit()
        session.refresh(blog_tag)

        return blog_tag
    
    @staticmethod
    def update_blog_tag(session: Session, blog_tag: BlogTag, blog_tag_data: TagCreate):

        blog_tag_data = blog_tag_data.model_dump()
        name = blog_tag_data["name"].lower().strip()
        slug = slugify(name)

        existing_tag = session.exec(select(BlogTag).where(BlogTag.slug == slug)).first()

        if existing_tag and existing_tag.id != blog_tag.id:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Tag already exists."
            )
        
        blog_tag = BlogTag(
            name = name,
            slug = slug
        )

        session.add(blog_tag)
        session.commit()
        session.refresh(blog_tag)
        
        return blog_tag
    
    @staticmethod
    def delete_blog_tag_by_slug(session: Session, blog_tag_slug: str):

        blog_tag = BlogPostService.get_blog_tag_by_slug(session, blog_tag_slug)

        session.delete(blog_tag)
        session.commit()

        return None

    @staticmethod
    def get_blog_posts(session: Session, q: str | None = None, page : int = 1, page_size : int = settings.DEFAULT_PAGE_SIZE, sort: str = "id"):


        offset = (page - 1) * page_size
            
        if q:

            statement = select(BlogPost).where(or_(BlogPost.title.icontains(q), BlogPost.body.icontains(q)))
            count_statement = select(func.count(BlogPost.id)).where(or_(BlogPost.title.icontains(q), BlogPost.body.icontains(q)))
        else:

            statement = select(BlogPost)
            count_statement = select(func.count(BlogPost.id))

        
        sort_field = sort.replace("-", "") if sort else None

        order_by = getattr(BlogPost, sort_field, None) if sort_field else None
        
        if order_by:

            order_by = order_by.desc() if sort.startswith("-") else order_by

    
        statement = statement.offset(offset).limit(page_size).order_by(order_by)

        count = session.exec(count_statement).one()

        blog_posts = session.exec(statement).all()

        return blog_posts, count
    
    @staticmethod
    def get_blog_post_by_slug(session: Session, slug: str):

        blog_post = session.exec(select(BlogPost).where(BlogPost.slug == slug).options(
            selectinload(BlogPost.tags), selectinload(BlogPost.author)
        )).one_or_none()

        if not blog_post:

            raise HTTPException(
                status_code = status.HTTP_200_OK,
                detail = f"Blog post with slug {slug} not found."
            )
        
        return blog_post
    
    @staticmethod
    def get_blog_post_by_id(session: Session, blog_post_id: int):

        blog_post = session.get(BlogPost, blog_post_id)

        if not blog_post:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Blog post with id {blog_post_id} was not found."
            )
            
        return blog_post
    
    @staticmethod
    def get_blog_posts_by_tag_slug(session: Session, slug: str, page : int = 1, page_size : int = settings.DEFAULT_PAGE_SIZE, sort: str = "id"):

        offset = (page - 1) * page_size


        statement = select(BlogPost).where(BlogPost.tags.any(BlogTag.slug == slug))

        sort_field = sort.replace("-", "") if sort else None

        order_by = getattr(BlogPost, sort_field, None) if sort_field else None
        
        if order_by:

            order_by = order_by.desc() if sort.startswith("-") else order_by

        statement = statement.offset(offset).limit(page_size).order_by(order_by)
        count_statement = select(func.count(BlogPost.id)).where(BlogPost.tags.any(BlogTag.slug == slug))
        blog_posts = session.exec(statement).all()
        count = session.exec(count_statement).first()
        

        return blog_posts, count
    

    def get_tags(session: Session, q: str | None = None, page : int = 1, page_size : int = settings.DEFAULT_PAGE_SIZE, sort: str = "id"):

        offset = (page - 1) * page_size
            
        if q:

            statement = select(BlogTag).where(or_(BlogTag.name.icontains(q), BlogTag.slug.icontains(q)))
            count_statement = select(func.count(BlogTag.id)).where(or_(BlogTag.name.icontains(q), BlogTag.slug.icontains(q)))
        else:

            statement = select(BlogTag)
            count_statement = select(func.count(BlogTag.id))

        
        sort_field = sort.replace("-", "") if sort else None

        order_by = getattr(BlogTag, sort_field, None) if sort_field else None
        
        if order_by:

            order_by = order_by.desc() if sort.startswith("-") else order_by

    
        statement = statement.offset(offset).limit(page_size).order_by(order_by)

        count = session.exec(count_statement).first()

        blog_tags = session.exec(statement).all()

        return blog_tags, count
    
    @staticmethod
    def get_blog_tag_by_slug(session: Session, blog_tag_slug: str):

        statement = select(BlogTag).where(BlogTag.slug == blog_tag_slug)
        blog_tag = session.exec(statement).first()

        if not blog_tag:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "No tag with slug: {blog_tag_slug} found."
            )

        return blog_tag

    @staticmethod
    def update_blog_post(session: Session, blog_post: BlogPost, blog_post_data: BlogPostUpdate | BlogPostPublish):

        blog_post_data = blog_post_data.model_dump(exclude_unset=True, exclude_none = True)

        blog_tags_data = blog_post_data.pop("tags", [])

        if blog_post_data.get("publishing_status", None) == PublishingStatus.PUBLISHED:

            blog_post.published_at = datetime.now(timezone.utc)

        if blog_post_data.get("title", None):

            blog_post_data["slug"] = slugify(blog_post_data['title'])

        for field, value in blog_post_data.items():
        
            setattr(blog_post, field, value)

        if len(blog_tags_data) > 0:

            blog_post.tags.clear()

            for tag_name in blog_tags_data:

                tag_name = tag_name.lower()
                tag_slug = slugify(tag_name)

                existing_tag = session.exec(select(BlogTag).where(BlogTag.slug == tag_slug)).one_or_none()

                if existing_tag:

                    blog_post.tags.append(existing_tag)

                else:

                    created_tag = BlogTag(name = tag_name, slug = tag_slug)
                    session.add(created_tag)
                    session.commit()
                    session.refresh(created_tag)
                    blog_post.tags.append(created_tag)
        
        session.add(blog_post)
        session.commit()
        session.refresh(blog_post)

        return blog_post
    
    @staticmethod
    def delete_blog_post(session: Session, blog_post: BlogPost):

        session.delete(blog_post)
        session.commit()

    @staticmethod
    def get_blog_post_comments(session: Session, blog_post_id: int, q: str | None = None, page : int = 1, page_size : int = settings.DEFAULT_PAGE_SIZE, sort: str = "-created_at"):

        
        offset = (page - 1) * page_size

        if q:

            statement = select(BlogComment).where(BlogComment.blog_post_id == blog_post_id).where(or_(BlogComment.body.icontains(q), )).options(
                selectinload(BlogComment.author)
            )
            count_statement = select(func.count(BlogComment.id)).where(BlogComment.blog_post_id == blog_post_id).where(or_(BlogComment.body.icontains(q), ))
        else:

            statement = select(BlogComment).where(BlogComment.blog_post_id == blog_post_id).options(
                selectinload(BlogComment.author)
            )
            count_statement = select(func.count(BlogComment.id)).where(BlogComment.blog_post_id == blog_post_id)

        
        sort_field = sort.replace("-", "") if sort else None

        order_by = getattr(BlogComment, sort_field, None) if sort_field else None
        
        if order_by:

            order_by = order_by.desc() if sort.startswith("-") else order_by

    
        statement = statement.offset(offset).limit(page_size).order_by(order_by)

        count = session.exec(count_statement).first()

        blog_comments = session.exec(statement).all()

        return blog_comments, count
    
    @staticmethod
    def create_blog_post_comment(session: Session, blog_post_id: int, current_user_id: int, blog_comment_data: BlogCommentCreate):

        blog_comment_data = blog_comment_data.model_dump(exclude_unset=True, exclude_none = True)
        blog_comment = BlogComment(**blog_comment_data)

        blog_comment.author_id = current_user_id
        blog_comment.blog_post_id = blog_post_id

        session.add(blog_comment)
        session.commit()
        session.refresh(blog_comment)

        return blog_comment
    
    @staticmethod
    def delete_blog_post_comment(session: Session, blog_comment_id: int):

        blog_comment = session.exec(select(BlogComment).where(BlogComment.id == blog_comment_id)).first()

        if not blog_comment:

            return None
        
        session.delete(blog_comment)
        session.commit()

        return None