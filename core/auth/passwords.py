import bcrypt

def hash_password(password: str) -> str:

    password = password.encode('utf-8')

    hashed_password = bcrypt.hashpw(
        password, 
        bcrypt.gensalt(15)
    )

    hashed_password = hashed_password.decode('utf-8')

    return hashed_password

def check_password(password: str, hashed_password: str) -> bool:

    password = password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password, hashed_password)