from sqlmodel import SQLModel
from ...models.auth.permission import PermissionCondition, PermissionAction
from ...models.auth.user import User
from ...models.auth.permission import Permission
from ...models.auth.role import Role, RoleName
from ...models.blog.comment import BlogComment
from ...models.blog.post import BlogPost, PublishingStatus
from ...models.blog.tag import BlogTag


from enum import Enum

class OwnerField(str, Enum):

    AUTHOR: str = 'author_id'
    USER: str = 'user_id'

class ResourceType(str, Enum):

    USER: str = User.__tablename__
    PERMISSION: str = Permission.__tablename__
    ROLE: str = Role.__tablename__
    POST: str = BlogPost.__tablename__
    TAG: str = BlogTag.__tablename__
    COMMENT: str = BlogComment.__tablename__



class PermissionEvaluator:



    @staticmethod
    def check_condition(user: User, item: SQLModel, condition: PermissionCondition) -> bool:

        if condition == PermissionCondition.ALWAYS:

            return True

        if condition == PermissionCondition.OWNER:

            for field in OwnerField:

                if getattr(item, field.value, None) == user.id:

                    return True

        if condition == PermissionCondition.SELF:
            
            return getattr(item, "id", None) == user.id
        
        if condition == PermissionCondition.SUPERIOR:

            return user.get_highest_rank() > item.get_highest_rank()
        
        if condition == PermissionCondition.SELF_OR_SUPERIOR:

            user_rank =  user.get_highest_rank() 
            other_user_rank = item.get_highest_rank()

            is_higher_rank = user_rank > other_user_rank

            return getattr(item, "id", None) == user.id or is_higher_rank

        return False
    
    
    @staticmethod
    def has_permission(user: User, action: PermissionAction, resource: ResourceType) -> bool:

        permissions = []

        if not user:

            return False
        
        for role in user.roles:

            for permission in role.permissions:

                if permission.action == action and permission.resource == resource and permission.condition == PermissionCondition.ALWAYS:

                    return True
                
        return False
        
    
    
    @staticmethod
    def has_object_permission(
        user: User, 
        action: PermissionAction, 
        resource: ResourceType, 
        item: SQLModel) -> bool:
    
        if action == PermissionAction.READ_DRAFT:

   
            return item.publishing_status == PublishingStatus.PUBLISHED
        
        if not user or not item:

            return False

        for role in user.roles:

            for permission in role.permissions:

                if permission.action == action and permission.resource == resource:

                    passed_condition_check = PermissionEvaluator.check_condition(user, item, permission.condition)

                    if passed_condition_check:

                        return True           
        
        return False