from ..models.authentication.models import Role, Permission, User
from sqlmodel import Session, select
from ..config import settings
from ..core import utils
from pydantic import EmailStr
import os

from ..models.authentication.models import Role, Permission, User, UserRoleLink
from sqlmodel import Session, select
from ..config import settings
from ..core import utils
from pydantic import EmailStr
import os

ADMIN = "admin"
SUPER_ADMIN = "super_admin"

CREATE = "create"
READ = "read"
UPDATE = "update"
DELETE = "delete"
LIST = "list"
IMPERSONATE = "impersonate"
ASSIGN = "assign"
REVOKE = "revoke"
ACTIVATE = "activate"

ALWAYS = 'always'
OWNER = 'owner'

USER = User.__tablename__
ROLE = Role.__tablename__
PERMISSION = Permission.__tablename__

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

        return True

    def create_permissions(self):
        permissions_data = [
            (CREATE, PERMISSION, 'Create permissions', ALWAYS),
            (READ, PERMISSION, 'Read permissions', ALWAYS),
            (UPDATE, PERMISSION, 'Update permission data', ALWAYS),
            (DELETE, PERMISSION, 'Delete permissions', ALWAYS),
            (LIST, PERMISSION, 'List permissions', ALWAYS),
            (ASSIGN, PERMISSION, 'Assign permissions', ALWAYS),
            (REVOKE, PERMISSION, 'Revoke permissions', ALWAYS),
            (CREATE, ROLE, 'Create roles', ALWAYS),
            (READ, ROLE, 'Create role', ALWAYS),
            (UPDATE, ROLE, 'Update role data', ALWAYS),
            (DELETE, ROLE, 'Delete role data', ALWAYS),
            (LIST, ROLE, 'List roles', ALWAYS),
            (ASSIGN, ROLE, 'Assign roles', ALWAYS),
            (REVOKE, ROLE, 'Revoke roles', ALWAYS),
            (CREATE, USER, 'Create users', ALWAYS),
            (READ, USER, 'Read user data', ALWAYS),
            (UPDATE, USER, 'Update user data', ALWAYS),
            (DELETE, USER, 'Delete users', ALWAYS),
            (LIST, USER, 'List users', ALWAYS),
            (IMPERSONATE, USER, 'Impersonate users', ALWAYS),
            (ACTIVATE, USER, 'Activate/deactivate users', ALWAYS),
            (READ, USER, "Read their own profile", OWNER),
            (UPDATE, USER, "Update their own profile", OWNER),
            (DELETE, USER, "Delete their own profile", OWNER)
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
            "super_admin": ("Ultimate system control - can do anything.", "ALL"),
            "admin":("User administration - can create, read, update and delete users, roles, and permissions", [
                (CREATE, USER, ALWAYS), (READ, USER, ALWAYS), (UPDATE, USER, ALWAYS), 
                (DELETE, USER, ALWAYS), (LIST, USER, ALWAYS), (ACTIVATE, USER, ALWAYS), 
                (IMPERSONATE, USER, ALWAYS),
                (CREATE, ROLE, ALWAYS), (READ, ROLE, ALWAYS), (UPDATE, ROLE, ALWAYS), (DELETE, ROLE, ALWAYS),
                (LIST, ROLE, ALWAYS), (REVOKE, ROLE, ALWAYS), (ASSIGN, ROLE, ALWAYS),
                (CREATE, PERMISSION, ALWAYS), (READ, PERMISSION, ALWAYS), 
                (UPDATE, PERMISSION, ALWAYS), (DELETE, PERMISSION, ALWAYS),
                (LIST,PERMISSION, ALWAYS), (ASSIGN, PERMISSION, ALWAYS),
                (REVOKE, PERMISSION, ALWAYS)
            ]),
            "user":("Normal user - can read, update, and delete their own profile.", [
                (READ, USER, OWNER), (UPDATE, USER, OWNER)
            ])
        }

        for name, (description, permissions) in roles_data.items():
            existing = self.session.exec(select(Role).where(Role.name == name)).first()
            if not existing:
                self._create_role(name, description, permissions)
    
    def _create_permission(self, name: str, action: str, description: str, resource: str, condition: str) -> Permission:
        permission = Permission(name=name, action=action, description=description, resource=resource, condition=condition)
        self.session.add(permission)
        self.session.commit()
        return permission

    def _create_role(self, name: str, description: str, permissions: list | tuple):
        role = Role(name=name, description=description)
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
        hashed_password = utils.hash_password(password)
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
            return self._create_base_user(username, email, password, settings.DEFAULT_USER_ROLE)
        return existing_user

    def create_super_admin_user(self, username="super_admin", email="super_admin@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, settings.SUPER_ADMIN_USER_ROLE)
        return existing_user

    def create_admin_user(self, username="admin", email="admin@example.com", password="password"):
        existing_user = self.session.exec(select(User).where(User.username == username)).first()
        if not existing_user:
            return self._create_base_user(username, email, password, settings.ADMIN_USER_ROLE)
        return existing_user