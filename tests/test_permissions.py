from ..core.rbac.permission_evaluator import PermissionEvaluator
from ..models.auth.permission import PermissionAction

def test_basic_user_does_not_have_update_users_permission(rbac):
    
    basic_user = rbac.create_basic_user(
        username = "basic_user",
        email = "basic_user@example.com",
        password = 'password'
    )

    has_permission = PermissionEvaluator.has_permission(
        basic_user, 
        PermissionAction.UPDATE,
        basic_user.__tablename__
    )

    assert not has_permission

def test_basic_user_has_update_self_permission(rbac):

    basic_user = rbac.create_basic_user(
        username = "basic_user",
        email = "basic_user@example.com",
        password = 'password'
    )

    has_object_permission_if_owner = PermissionEvaluator.has_object_permission(
        basic_user, 
        PermissionAction.UPDATE,
        basic_user.__tablename__,
        basic_user
    )

    assert has_object_permission_if_owner == True

def test_basic_user_does_not_have_update_other_user_permission(rbac):

    basic_user = rbac.create_basic_user(
        username = "basic_user",
        email = "basic_user@example.com",
        password = 'password'
    )

    other_user = rbac.create_basic_user(
        username = f"other_{basic_user.username}",
        email = f"other_{basic_user.email}",
        password = 'password'
    )

    has_object_permission = PermissionEvaluator.has_object_permission(
        basic_user, 
        PermissionAction.UPDATE,
        basic_user.__tablename__,
        other_user
    )

    assert not has_object_permission
    

