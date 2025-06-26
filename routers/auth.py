# from fastapi import APIRouter, Depends, HTTPException, Response, Request
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from db.database import SessionLocal
# from db.models import User
# from schema.schemas import UserCreate, UserLogin, ForgotPassword, ResetPassword
# from utils.utils import (
#     hash_password, verify_password, create_session_token, verify_session_token
# )
# import secrets
#
# router = APIRouter()
#
# COOKIE_NAME = "session_token"
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# @router.post("/signup")
# def signup(user: UserCreate, response: Response, db: Session = Depends(get_db)):
#     if db.query(User).filter(User.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already registered")
#     if db.query(User).filter(User.username == user.username).first():
#         raise HTTPException(status_code=400, detail="Username already taken")
#
#     db_user = User(
#         email=user.email,
#         username=user.username,
#         hashed_password=hash_password(user.password),
#         role="user",
#         provider="local"
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#
#     session_token = create_session_token(db_user.email, db_user.role)
#     response.set_cookie(
#         key=COOKIE_NAME,
#         value=session_token,
#         httponly=True,
#         samesite="Lax"
#     )
#     return {"message": "Signup successful", "email": db_user.email, "role": db_user.role}
#
# @router.post("/login")
# def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.email == user.email).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     session_token = create_session_token(db_user.email, db_user.role)
#     response.set_cookie(
#         key=COOKIE_NAME,
#         value=session_token,
#         httponly=True,
#         samesite="Lax"
#     )
#     return {"message": "Login successful", "email": db_user.email, "role": db_user.role}
#
# @router.post("/logout")
# def logout(response: Response):
#     response.delete_cookie(COOKIE_NAME)
#     return {"message": "Logged out successfully"}
#
# @router.get("/me")
# def get_me(request: Request, db: Session = Depends(get_db)):
#     session_token = request.cookies.get(COOKIE_NAME)
#     if not session_token:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#
#     payload = verify_session_token(session_token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid session")
#
#     user = db.query(User).filter(User.email == payload["sub"]).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     return {"email": user.email, "username": user.username, "role": user.role}
#
# @router.post("/forgot-password")
# def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == payload.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Email not found")
#
#     token = secrets.token_urlsafe(32)
#     user.reset_token = token
#     db.commit()
#     return {"reset_token": token}
#
# @router.post("/reset-password")
# def reset_password(payload: ResetPassword, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.reset_token == payload.token).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid token")
#
#     user.hashed_password = hash_password(payload.new_password)
#     user.reset_token = None
#     db.commit()
#     return {"message": "Password reset successful"}


"""
this older version - 25/06/25
"""

#
# from fastapi import APIRouter, Depends, HTTPException, Response, Request
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# from db.database import SessionLocal
# from db.models import User
# from schema.schemas import UserCreate, UserLogin, ForgotPassword, ResetPassword
# from utils.utils import hash_password, verify_password, create_session_token, verify_session_token
# from core.custom_exception import CustomAPIException
# import secrets
# from db.models import Base
# from db.database import engine
#
# router = APIRouter()
# COOKIE_NAME = "session_token"
#
# Base.metadata.create_all(bind=engine)
#
# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# # Signup endpoint
# @router.post("/signup")
# def signup(user: UserCreate, response: Response, db: Session = Depends(get_db)):
#     if db.query(User).filter(User.email == user.email).first():
#         raise CustomAPIException("E_SIGNUP_DUPLICATE", "Email already registered")
#     if db.query(User).filter(User.username == user.username).first():
#         raise CustomAPIException("E_SIGNUP_DUPLICATE", "Username already taken")
#
#     db_user = User(
#         email=user.email,
#         username=user.username,
#         hashed_password=hash_password(user.password),
#         role="user",
#         provider="local"
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#
#     session_token = create_session_token(db_user.email, db_user.role)
#     response.set_cookie(key=COOKIE_NAME, value=session_token, httponly=True, samesite="Lax")
#     return {"success": True, "email": db_user.email, "role": db_user.role}
#
# # Login endpoint
# @router.post("/login")
# def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.email == user.email).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise CustomAPIException("E_AUTH_FAILED", "Invalid credentials", status_code=401)
#
#     session_token = create_session_token(db_user.email, db_user.role)
#     response.set_cookie(key=COOKIE_NAME, value=session_token, httponly=True,secure=True, samesite="None" )
#     return {"success": True, "email": db_user.email, "role": db_user.role}
#
# # Logout
# @router.post("/logout")
# def logout(response: Response):
#     response.delete_cookie(COOKIE_NAME)
#     return {"message": "Logged out successfully"}
#
# # Get current user
# @router.get("/me")
# def get_me(request: Request, db: Session = Depends(get_db)):
#     session_token = request.cookies.get(COOKIE_NAME)
#     if not session_token:
#         raise CustomAPIException("E_AUTH_MISSING", "Session token missing", 401)
#
#     payload = verify_session_token(session_token)
#     if not payload:
#         raise CustomAPIException("E_TOKEN_INVALID", "Invalid or expired session token", 401)
#
#     user = db.query(User).filter(User.email == payload["sub"]).first()
#     if not user:
#         raise CustomAPIException("E_USER_NOT_FOUND", "User not found", 404)
#
#     return {"success": True, "email": user.email, "username": user.username, "role": user.role}
#
# # Forgot Password
# @router.post("/forgot-password")
# def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == payload.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Email not found")
#
#     token = secrets.token_urlsafe(32)
#     user.reset_token = token
#     db.commit()
#     return {"reset_token": token}
#
# # Reset Password
# @router.post("/reset-password")
# def reset_password(payload: ResetPassword, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.reset_token == payload.token).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid token")
#
#     user.hashed_password = hash_password(payload.new_password)
#     user.reset_token = None
#     db.commit()
#     return {"message": "Password reset successful"}



# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request, Cookie
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User
from schema.schemas import UserCreate, UserLogin, ForgotPassword, ResetPassword
from utils.utils import hash_password, verify_password, create_session_token, verify_session_token
from core.custom_exception import CustomAPIException
import secrets
from sqlalchemy import create_engine
from db.models import Base
from db.database import engine

Base.metadata.create_all(bind=engine)

router = APIRouter()
COOKIE_NAME = "session_token"

def get_db():
    db = SessionLocal();
    try: yield db
    finally: db.close()

@router.post("/signup")
def signup(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        raise CustomAPIException("E_SIGNUP_DUPLICATE", "Email already registered")
    if db.query(User).filter_by(username=user.username).first():
        raise CustomAPIException("E_SIGNUP_DUPLICATE", "Username already taken")

    db_user = User(
        email=user.email, username=user.username,
        hashed_password=hash_password(user.password),
        provider="local", role="user"
    )
    db.add(db_user); db.commit(); db.refresh(db_user)

    token = create_session_token(db_user.email, db_user.role)
    response.set_cookie(
        key=COOKIE_NAME, value=token,
        httponly=True, secure=True, samesite="None"
    )
    return {"message": "Signup successful", "email": db_user.email, "role": db_user.role}

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise CustomAPIException("E_AUTH_FAILED", "Invalid credentials", status_code=401)

    token = create_session_token(db_user.email, db_user.role)
    response.set_cookie(
        key=COOKIE_NAME, value=token,
        httponly=True, secure=True, samesite="None"
    )
    return {"message": "Login successful", "email": db_user.email, "role": db_user.role}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"message": "Logged out successfully"}

@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise CustomAPIException("E_AUTH_MISSING", "Not authenticated", 401)

    payload = verify_session_token(token)
    if not payload:
        raise CustomAPIException("E_TOKEN_INVALID", "Invalid token", 401)

    user = db.query(User).filter_by(email=payload["sub"]).first()
    if not user:
        raise CustomAPIException("E_USER_NOT_FOUND", "User not found", 404)

    return {"email": user.email, "username": user.username, "role": user.role}

@router.post("/forgot-password")
def forgot_password(p: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=p.email).first()
    if not user:
        raise CustomAPIException("E_NOT_FOUND", "Email not found", status_code=404)
    token = secrets.token_urlsafe(32)
    user.reset_token = token; db.commit()
    return {"reset_token": token}

@router.post("/reset-password")
def reset_password(p: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(reset_token=p.token).first()
    if not user:
        raise CustomAPIException("E_INVALID_TOKEN", "Invalid token", status_code=400)
    user.hashed_password = hash_password(p.new_password)
    user.reset_token = None; db.commit()
    return {"success": True}
