from ...database.db import get_session
from fastapi import Depends, status, Request, HTTPException
from sqlmodel import Session, select, SQLModel
from ...models.auth.user import User
from ...models.auth.permission import Permission, PermissionAction
from ...models.auth.role import Role
from ...models.blog.post import BlogPost
from ...models.blog.tag import BlogTag
from ...models.blog.comment import BlogComment
from ...core.auth.dependecies import get_current_user
from .permission_evaluator import PermissionEvaluator
from typing import Optional

USER = User.__tablename__
ROLE = Role.__tablename__
PERMISSION = Permission.__tablename__
BLOG_POST = BlogPost.__tablename__
BLOG_TAG = BlogTag.__tablename__
BLOG_COMMENT = BlogComment.__tablename__

RESOURCE_NAME_TO_MODEL_MAPPING = {
    USER: User,
    ROLE: Role,
    PERMISSION: Permission,
    BLOG_POST: BlogPost,
    BLOG_TAG: BlogTag,
    BLOG_COMMENT:BlogComment
}

def get_resource_by_field(session: Session, Model: SQLModel, field: str, value: str):

    return session.exec(select(Model).where(getattr(Model, field, None) == value)).first()


def get_model_by_resource_name(resource_name):

    return RESOURCE_NAME_TO_MODEL_MAPPING[resource_name]


def require_permission(
        action: PermissionAction,
        resource: str, 
        lookup_field = Optional[str]):
    
    async def permission_checker(
            request: Request,
            current_user: User | None = Depends(get_current_user),
            session: Session = Depends(get_session)):
        
        if not current_user and action == PermissionAction.CREATE and resource == USER:

            return True
        
        elif not current_user and action != PermissionAction.READ_DRAFT:

            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "You are not authorized to perform this action."
            )
        
        has_permission = PermissionEvaluator.has_permission(current_user, action, resource)

        if has_permission:

            return has_permission
        
        if lookup_field:

            resource_identifier = request.path_params.get(lookup_field, None)

            obj = session.get(get_model_by_resource_name(resource), resource_identifier)

            has_object_permission = PermissionEvaluator.has_object_permission(current_user, action, resource, obj)

            if has_object_permission:

                return has_object_permission

        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action."
        )
    
    return permission_checker



