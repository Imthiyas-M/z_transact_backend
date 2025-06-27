from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os, hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "zLiPd1TMs5GtHM4x89ucbc3VW5LmtqiOjgdz15fHyMU"
ALGORITHM = "HS256"
SESSION_EXPIRE_MINUTES = 60

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_session_token(email: str, role: str):
    expire = datetime.utcnow() + timedelta(minutes=SESSION_EXPIRE_MINUTES)
    return jwt.encode({
        "sub": email,
        "role": role,
        "exp": expire
    }, SECRET_KEY, algorithm=ALGORITHM)

def verify_session_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # contains "sub" and "role"
    except JWTError:
        return None

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def hash_file(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()



# from jose import jwt, JWTError
# from datetime import datetime, timedelta
# from datetime import datetime, timedelta
# from passlib.context import CryptContext
#
# SECRET_KEY = "iiy90UMOx_bbhhhCj5s7M3cAPBIShUAEXME5fXaoMks"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_DAYS = 7
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)
#
# def create_session_token(email: str, role: str, expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)) -> str:
#     payload = {
#         "sub": email,
#         "role": role,
#         "exp": datetime.utcnow() + expires_delta
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#
# def verify_session_token(token: str):
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.PyJWTError:
#         return None
