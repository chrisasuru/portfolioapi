from sqlmodel import SQLModel, Field

class RolePermissionLink(SQLModel, table = True):

    role_id: int = Field(default = None, foreign_key = "role.id", primary_key=True)
    permission_id: int = Field(default = None, foreign_key = "permission.id", primary_key = True)


class UserRoleLink(SQLModel, table = True):

    user_id: int = Field(default = None, foreign_key = "user.id", primary_key = True)
    role_id: int = Field(default = None, foreign_key = "role.id", primary_key = True)
