from ..models.auth.user import User 
from ..models.auth.permission import Permission, PermissionAction, PermissionCondition
from ..models.auth.role import Role, RoleName, RoleRank
from ..models.blog.tag import BlogTag
from ..models.blog.comment import BlogComment
from ..models.blog.post import BlogPost
from sqlmodel import Session, select, func
from ..config import settings
from ..core.auth.passwords import hash_password
from pydantic import EmailStr
from slugify import slugify
from faker import Faker
from sqlalchemy.exc import IntegrityError
from random import choice, choices
import os

USER = User.__tablename__
ROLE = Role.__tablename__
PERMISSION = Permission.__tablename__
BLOG_TAG = BlogTag.__tablename__
BLOG_COMMENT = BlogComment.__tablename__
BLOG_POST = BlogPost.__tablename__



class RBACInitializer:

    def __init__(self, session: Session):
        self.session = session

    def populate(self):
        self.create_permissions()
        self.create_roles()

        # You must also create the users here to ensure they are created in the same session
        self.create_super_admin_user()
        self.create_admin_user()
        self.create_basic_user()
        self.create_editor_user()
        self.create_publisher_user()

        return True

    def create_permissions(self):
        permissions_data = [
            (PermissionAction.CREATE, PERMISSION, 'Create permissions', PermissionCondition.ALWAYS),
            (PermissionAction.READ, PERMISSION, 'Read permissions', PermissionCondition.ALWAYS),
            (PermissionAction.UPDATE, PERMISSION, 'Update permission data', PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, PERMISSION, 'Delete permissions', PermissionCondition.ALWAYS),
            (PermissionAction.LIST, PERMISSION, 'List permissions', PermissionCondition.ALWAYS),
            (PermissionAction.ASSIGN, PERMISSION, 'Assign permissions', PermissionCondition.ALWAYS),
            (PermissionAction.REVOKE, PERMISSION, 'Revoke permissions', PermissionCondition.ALWAYS),
            (PermissionAction.CREATE, ROLE, 'Create roles', PermissionCondition.ALWAYS),
            (PermissionAction.READ, ROLE, 'Create role', PermissionCondition.ALWAYS),
            (PermissionAction.UPDATE, ROLE, 'Update role data', PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, ROLE, 'Delete role data', PermissionCondition.ALWAYS),
            (PermissionAction.LIST, ROLE, 'List roles', PermissionCondition.ALWAYS),
            (PermissionAction.ASSIGN, ROLE, 'Assign roles', PermissionCondition.ALWAYS),
            (PermissionAction.REVOKE, ROLE, 'Revoke roles', PermissionCondition.ALWAYS),
            (PermissionAction.CREATE, USER, 'Create users', PermissionCondition.ALWAYS),
            (PermissionAction.READ, USER, 'Read user data', PermissionCondition.ALWAYS),
            (PermissionAction.UPDATE, USER, 'Update user data', PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, USER, 'Delete users', PermissionCondition.ALWAYS),
            (PermissionAction.LIST, USER, 'List users', PermissionCondition.ALWAYS),
            (PermissionAction.IMPERSONATE, USER, 'Impersonate users', PermissionCondition.ALWAYS),
            (PermissionAction.ACTIVATE, USER, 'Activate/deactivate users', PermissionCondition.ALWAYS),
            (PermissionAction.READ, USER, 'Read inferior user data', PermissionCondition.SELF_OR_SUPERIOR),
            (PermissionAction.UPDATE, USER, 'Update inferior user data', PermissionCondition.SELF_OR_SUPERIOR),
            (PermissionAction.DELETE, USER, 'Delete inferior users', PermissionCondition.SELF_OR_SUPERIOR),
            (PermissionAction.READ, USER, "Read their own profile", PermissionCondition.SELF),
            (PermissionAction.UPDATE, USER, "Update their own profile", PermissionCondition.SELF),
            (PermissionAction.DELETE, USER, "Delete their own profile", PermissionCondition.SELF),
            (PermissionAction.CREATE, BLOG_TAG, "Create blog tags", PermissionCondition.ALWAYS),
            (PermissionAction.UPDATE, BLOG_TAG, "Update blog tags", PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, BLOG_TAG, "Delete blog tags", PermissionCondition.ALWAYS),
            (PermissionAction.CREATE, BLOG_COMMENT, "Comment on blogs", PermissionCondition.ALWAYS),
            (PermissionAction.UPDATE, BLOG_COMMENT, "Update blog comments", PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, BLOG_COMMENT, "Delete blog comments", PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, BLOG_COMMENT, "Delete their own blog comments", PermissionCondition.OWNER),
            (PermissionAction.CREATE, BLOG_POST, "Create blog posts", PermissionCondition.ALWAYS),
            (PermissionAction.CREATE_DRAFT, BLOG_POST, "Create blog post drafts", PermissionCondition.ALWAYS),
            (PermissionAction.READ_DRAFT, BLOG_POST, "Read blog post drafts", PermissionCondition.ALWAYS),
            (PermissionAction.PUBLISH, BLOG_POST, "Update blog posts", PermissionCondition.ALWAYS),
            (PermissionAction.UPDATE, BLOG_POST, "Update blog posts", PermissionCondition.ALWAYS),
            (PermissionAction.DELETE, BLOG_POST, "Delete blog posts", PermissionCondition.ALWAYS),
        ]

        for action, resource, description, condition in permissions_data:
            name = f"{action}_{resource}_{condition}"
            existing = self.session.exec(
                select(Permission).where(Permission.name == name, Permission.resource == resource)
            ).first()
            if not existing:
                try:
                    permission = self._create_permission(name, action, description, resource, condition)
                    # No need to return anything, the method handles persistence
                except Exception as e:
                    print(e)
    
    def create_roles(self):
        roles_data = {
            RoleName.SUPER_ADMIN: ("Ultimate system control - can do anything.", "ALL", RoleRank.SUPER_ADMIN),
            RoleName.ADMIN:("User administration - can create, read, update and delete users, roles, and permissions", [
                (PermissionAction.CREATE, USER, PermissionCondition.ALWAYS), (PermissionAction.READ, USER, PermissionCondition.ALWAYS), (PermissionAction.UPDATE, USER, PermissionCondition.SELF_OR_SUPERIOR), 
                (PermissionAction.DELETE, USER, PermissionCondition.SELF_OR_SUPERIOR), (PermissionAction.LIST, USER, PermissionCondition.ALWAYS), (PermissionAction.ACTIVATE, USER, PermissionCondition.ALWAYS), 
                (PermissionAction.IMPERSONATE, USER, PermissionCondition.SUPERIOR),
                (PermissionAction.CREATE, ROLE, PermissionCondition.ALWAYS), (PermissionAction.READ, ROLE, PermissionCondition.ALWAYS), (PermissionAction.UPDATE, ROLE, PermissionCondition.ALWAYS), (PermissionAction.DELETE, ROLE, PermissionCondition.ALWAYS),
                (PermissionAction.LIST, ROLE, PermissionCondition.ALWAYS), (PermissionAction.REVOKE, ROLE, PermissionCondition.ALWAYS), (PermissionAction.ASSIGN, ROLE, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, PERMISSION, PermissionCondition.ALWAYS), (PermissionAction.READ, PERMISSION, PermissionCondition.ALWAYS), 
                (PermissionAction.UPDATE, PERMISSION, PermissionCondition.ALWAYS), (PermissionAction.DELETE, PERMISSION, PermissionCondition.ALWAYS),
                (PermissionAction.LIST,PERMISSION, PermissionCondition.ALWAYS), (PermissionAction.ASSIGN, PERMISSION, PermissionCondition.ALWAYS),
                (PermissionAction.REVOKE, PERMISSION, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, BLOG_TAG, PermissionCondition.ALWAYS), (PermissionAction.UPDATE, BLOG_TAG, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_TAG, PermissionCondition.ALWAYS), (PermissionAction.CREATE, BLOG_COMMENT, PermissionCondition.ALWAYS),
                (PermissionAction.UPDATE, BLOG_COMMENT, PermissionCondition.ALWAYS), (PermissionAction.DELETE, BLOG_COMMENT, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, BLOG_POST, PermissionCondition.ALWAYS), (PermissionAction.UPDATE, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_POST, PermissionCondition.ALWAYS), (PermissionAction.CREATE_DRAFT, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.READ_DRAFT, BLOG_POST, PermissionCondition.ALWAYS), (PermissionAction.PUBLISH, BLOG_POST, PermissionCondition.ALWAYS),
            ], RoleRank.ADMIN),
            RoleName.PUBLISHER: ("Publisher - can read, update, and publish draft blog posts.", [
                (PermissionAction.CREATE_DRAFT, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.READ_DRAFT, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.PUBLISH, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, BLOG_POST, PermissionCondition.ALWAYS),               
                (PermissionAction.UPDATE, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, BLOG_TAG, PermissionCondition.ALWAYS), 
                (PermissionAction.UPDATE, BLOG_TAG, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_TAG, PermissionCondition.ALWAYS), 
            ], RoleRank.PUBLISHER),
            RoleName.EDITOR: ("Editor - can update and delete blog posts.", [  
                (PermissionAction.CREATE_DRAFT, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.READ_DRAFT, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.PUBLISH, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, BLOG_POST, PermissionCondition.ALWAYS),           
                (PermissionAction.UPDATE, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_POST, PermissionCondition.ALWAYS),
                (PermissionAction.CREATE, BLOG_TAG, PermissionCondition.ALWAYS), 
                (PermissionAction.UPDATE, BLOG_TAG, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_TAG, PermissionCondition.ALWAYS), 
            ], RoleRank.EDITOR),
            RoleName.USER:("Normal user - can read, update, and delete their own profile and create and delete comments on blog posts", [
                (PermissionAction.READ, USER, PermissionCondition.SELF), 
                (PermissionAction.UPDATE, USER, PermissionCondition.SELF),
                (PermissionAction.DELETE, USER, PermissionCondition.SELF),
                (PermissionAction.CREATE, BLOG_COMMENT, PermissionCondition.ALWAYS),
                (PermissionAction.DELETE, BLOG_COMMENT, PermissionCondition.OWNER)
            ], RoleRank.USER)
        }

        for name, (description, permissions, rank) in roles_data.items():
          
            existing = self.session.exec(select(Role).where(Role.name == name)).first()
            if not existing:
                self._create_role(name, description, permissions, rank)
    
    def _create_permission(self, name: str, action: str, description: str, resource: str, condition: str) -> Permission:
        permission = Permission(name=name, action=action, description=description, resource=resource, condition=condition)
        self.session.add(permission)
        self.session.commit()
        return permission

    def _create_role(self, name: str, description: str, permissions: list | tuple, rank: int):

        role = Role(name=name, description=description, rank=rank)
        self.session.add(role) # Add the role to the session before assigning permissions
        self.session.commit()
        
        if permissions != "ALL":
            for action, resource, condition in permissions:
                permission_name = f"{action}_{resource}_{condition}"
                statement = select(Permission).where(
                    Permission.name == permission_name, 
                    Permission.action == action, 
                    Permission.resource == resource,
                    Permission.condition == condition
                )
                permission = self.session.exec(statement).first()
                if permission:
                    # Append the permission using the relationship list
                    role.permissions.append(permission)
        else:
            
            permissions = self.session.exec(select(Permission)).all()
            for permission in permissions:

                role.permissions.append(permission)
            
        # We need to commit again to save the permissions added to the role
        self.session.commit()
        return role

    def _create_base_user(self, username: str, email: EmailStr, password: str, role_name: str):
        hashed_password = hash_password(password)
        user = User(username=username, email=email, password=hashed_password)
        
        role = self.session.exec(select(Role).where(Role.name == role_name)).first()
        if role:
            # Append the role to the user's roles relationship list
            user.roles.append(role)
        
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_basic_user(self, username="user", email="user@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, RoleName.USER)
        return existing_user

    def create_super_admin_user(self, username="super_admin", email="super_admin@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, RoleName.SUPER_ADMIN)
        return existing_user

    def create_admin_user(self, username="admin", email="admin@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, RoleName.ADMIN)
        return existing_user
    
    def create_publisher_user(self, username="publisher", email="publisher@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, RoleName.PUBLISHER)
        return existing_user
    
    def create_editor_user(self, username="editor", email="editor@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, RoleName.EDITOR)
        return existing_user



class BlogInitializer:


    def __init__(self, session: Session):

        self.session = session

    def populate(self):

        self.create_tags()
        self.create_blogs()

        return True
    
    def create_tags(self):

        for tag_name in settings.DEFAULT_BLOG_CATEGORIES:

            self.create_tag(tag_name)
    
    def create_tag(self, name: str):

        existing_tag = self.session.exec(select(BlogTag).where(BlogTag.name == name)).first()

        if not existing_tag:

            slug = slugify(name)

            tag = BlogTag(name = name, slug = slug)

            self.session.add(tag)
            self.session.commit()
            self.session.refresh(tag)

            return tag

        return existing_tag
    
    
    def create_blogs(self, count: int = 70):

        if not settings.DEBUG:

            return None
        
        blog_count = self.session.exec(select(func.count(BlogPost.id))).one()

        if blog_count > 0:

            return None
          
        faker = Faker()

        for step in range(count):
            title = faker.name()
            slug = slugify(title)
            body = "\n\n".join(faker.paragraphs(nb = 25))
            self.create_blog(title, slug, body)
    
    def create_blog(self, 
                    title: str, 
                    slug: str, 
                    body: str,
                    tag_names: list[str] = choices(settings.DEFAULT_BLOG_CATEGORIES, k = 2)):
        
        faker = Faker()
        username = faker.unique.user_name()
        email = faker.unique.email()
        hashed_password = hash_password(faker.password())
        first_name = faker.first_name()
        last_name = faker.last_name()

        user = User(username = username, email = email, password = hashed_password, first_name = first_name, last_name = last_name)
        self.session.add(user)
        self.session.commit()
        blog = BlogPost(title = title, slug = slug, body = body)
        blog.author_id = user.id

        for name in tag_names:
            tag = self.create_tag(name)

            if tag not in blog.tags:

                blog.tags.append(tag)                
                

        try:

            self.session.add(blog)
            self.session.commit()
            self.session.refresh(blog)

        except IntegrityError:

            self.session.rollback()
