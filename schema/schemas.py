from pydantic import BaseModel, EmailStr
from typing import List

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class UserOut(UserBase):
    role: str


class OAuthRequest(BaseModel):
    provider: str; code: str; code_verifier: str | None = None

class ConnectPayload(BaseModel):
    email: str; password: str; imap: dict; smtp: dict

class SyncPayload(BaseModel):
    email_connection_id: str
    auto_sync: bool; email_folders: List[str]; email_documents: List[str]; sync_interval: int
