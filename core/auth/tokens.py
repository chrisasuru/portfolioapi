from datetime import datetime, timezone, timedelta
from ...models.auth.user import User
from ...config import settings
import jwt

def generate_access_token(user : User):

    user_id = str(user.id)

    permissions = []

    for role in user.roles:
        for permission in role.permissions:
            permissions.append({"action": permission.action, "resource": permission.resource, "condition": permission.condition})
    
    rank = max([role.rank for role in user.roles])
    
    expires = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims = {
        "sub": user_id,
        "permissions": permissions,
        "rank": rank,
        "exp": expires,
        "iat": datetime(timezone.utc)
    }
    access_token = jwt.encode(
        claims,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return access_token
