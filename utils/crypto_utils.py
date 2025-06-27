# services/crypto_utils.py
import os
from cryptography.fernet import Fernet
from core.config import settings

key = settings.ENCRYPT_SECRET.encode() if settings.ENCRYPT_SECRET else Fernet.generate_key()
fernet = Fernet(key)

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return fernet.decrypt(encrypted_password.encode()).decode()
