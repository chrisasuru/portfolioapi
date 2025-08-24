from ..models.user import Role, Permission, ResourcePermission, User
from sqlmodel import Session, select
from ..config import settings
from ..core import utils
import os

CREATE = "create"
READ = "read"
UPDATE = "update"
DELETE = "delete"
LIST = "list"
IMPERSONATE = "impersonate"
ASSIGN = "assign"
REVOKE = "revoke"
ACTIVATE = "activate"

USER = User.__tablename__
ROLE = Role.__tablename__
PERMISSION = Permission.__tablename__
PROFILE = "profile"


class RBACInitializer:


    def __init__(self, session: Session):

        self.session = session

    def create_permissions(self):

        created_permissions = {}

        permissions_data = [
            (CREATE, PERMISSION, 'Create permissions'),
            (READ, PERMISSION, 'Read permissions'),
            (UPDATE, PERMISSION, 'Update permission data'),
            (DELETE, PERMISSION, 'Delete permissions'),
            (LIST, PERMISSION, 'List permissions'),
            (ASSIGN, PERMISSION, 'Assign permissions'),
            (REVOKE, PERMISSION, 'Revoke permissions'),
            (CREATE, ROLE, 'Create roles'),
            (READ, ROLE, 'Create role'),
            (UPDATE, ROLE, 'Update role data'),
            (DELETE, ROLE, 'Delete role data'),
            (LIST, ROLE, 'List roles'),
            (ASSIGN, ROLE, 'Assign roles'),
            (REVOKE, ROLE, 'Revoke roles'),
            (CREATE, USER, 'Create users'),
            (READ, USER, 'Read user data'),
            (UPDATE, USER, 'Update user data'),
            (DELETE, USER, 'Delete users'),
            (LIST, USER, 'List users'),
            (ACTIVATE, USER, 'Activate/deactivate users'),
            (READ, PROFILE, "Read their own profile"),
            (UPDATE, PROFILE, "Update their own profile")
        ]

        for action, resource, description in permissions_data:
            
            name = f"{action}_{resource}"
            existing = self.session.exec(select(Permission).where(Permission.name == name, Permission.resource == resource)).first()
        
            if not existing:
                try:

                    permission = self._create_permission(name, action, description, resource)
                except Exception as e:

                    print(e)
            created_permissions[name] = True
        
        return created_permissions
        
    
    def create_roles(self):

        created_roles = {}

        roles_data = {
            "super_admin": ("Ultimate system control - can do anything.", "ALL"),
            "admin":("User administration - can create, read, update and delete users, roles, and permissions", [
                (CREATE, USER), (READ, USER), (UPDATE, USER), 
                (DELETE, USER), (LIST, USER), (ACTIVATE, USER), 
                (READ, PROFILE), (UPDATE, PROFILE),
                (CREATE, ROLE), (READ, ROLE), (UPDATE, ROLE), (DELETE, ROLE),
                (LIST, ROLE), (REVOKE, ROLE), (ASSIGN, ROLE),
                (CREATE, PERMISSION), (READ, PERMISSION), 
                (UPDATE, PERMISSION), (DELETE, PERMISSION),
                (LIST,PERMISSION), (ASSIGN, PERMISSION),
                (REVOKE, PERMISSION)
            ]),
            "user":("Normal user - can read, update, and delete their own profile.", [
                (READ, PROFILE), (UPDATE, PROFILE)
            ])
            
        }

        for name, (description, permissions) in roles_data.items():


            existing = self.session.exec(select(Role).where(Role.name == name)).first()
            
            if not existing:
                
                role = self._create_role(name, description, permissions)

            created_roles[name] = True

        return created_roles
    
    def create_super_admin(self):

        role = self.session.exec(select(Role).where(Role.name == settings.SUPER_ADMIN_ROLE)).first()
        
        hashed_password = utils.hash_password('password')

        admin_exists = self.session.exec(select(User.username).where(User.username == 'admin')).first()

        if admin_exists:

            return

        admin = User(username = "admin", email = "admin@example.com", password = hashed_password)
        admin.roles.append(role)
        
        self.session.add(admin)
        self.session.commit()

    def _create_permission(self, name: str, action: str, description: str, resource:str) -> Permission:

        permission = Permission(name = name, action = action, description = description, resource = resource)
        self.session.add(permission)
        self.session.commit()

        return permission
    
    def _create_role(self, name: str, description: str, permissions : list | tuple):
 
        role = Role(name = name, description = description)

        if name != settings.SUPER_ADMIN_ROLE:

            for action, resource in permissions:

                permission_name = f"{action}_{resource}"


                permission = self.session.exec(select(Permission).where(Permission.name == permission_name, Permission.action == action, Permission.resource == resource)).first()
                role.permissions.append(permission)
        
        
        self.session.add(role)
        self.session.commit()

        return role
    



    


