import bcrypt
from ..config import settings

def hash_password(password: str) -> str:

    password = password.encode('utf-8')


    hashed_password = bcrypt.hashpw(
        password, 
        bcrypt.gensalt(15)
    )

    return hashed_password

def check_password(password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(password, hashed_password)
