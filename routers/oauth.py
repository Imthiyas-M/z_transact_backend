#
#
#
# import os, requests
# from fastapi import APIRouter, Depends, HTTPException, Response
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from dotenv import load_dotenv
# from db.database import SessionLocal
# from db.models import User
# from utils.utils import create_session_token
#
# load_dotenv()
# router = APIRouter()
# COOKIE_NAME = "session_token"
#
# # ✅ Input model with optional code_verifier for Microsoft PKCE
# class OAuthRequest(BaseModel):
#     provider: str
#     code: str
#     code_verifier: str | None = None
#
# # ✅ Dependency for DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# @router.post("/oauth")
# def oauth_login(payload: OAuthRequest, response: Response, db: Session = Depends(get_db)):
#     provider = payload.provider.lower()
#     code = payload.code
#     code_verifier = payload.code_verifier
#
#     if provider not in ["google", "github", "microsoft"]:
#         raise HTTPException(status_code=400, detail="Unsupported provider")
#
#     # Get user info from the respective provider
#     if provider == "google":
#         user_info = handle_google(code)
#     # elif provider == "github":
#     #     user_info = handle_github(code)
#     elif provider == "microsoft":
#         user_info = handle_microsoft(code, code_verifier)
#     else:
#         raise HTTPException(status_code=400, detail="Unsupported provider")
#
#     if not user_info:
#         raise HTTPException(status_code=400, detail="Failed to retrieve user info")
#
#     email = user_info.get("email")
#     if not email:
#         raise HTTPException(status_code=400, detail="Email not available from provider")
#
#     username = user_info.get("name") or email.split("@")[0]
#
#     # ✅ Wrap DB operations with error logging
#     try:
#         user = db.query(User).filter(User.email == email).first()
#         if not user:
#             user = User(email=email, username=username, provider=provider, role="user")
#             db.add(user)
#             db.commit()
#             db.refresh(user)
#     except Exception as e:
#         print("Database error:", e)
#         raise HTTPException(status_code=500, detail="Database error")
#
#     session_token = create_session_token(user.email, user.role)
#     response.set_cookie(key=COOKIE_NAME, value=session_token, httponly=True, samesite="Lax")
#
#     return {
#         "message": f"Login via {provider} successful",
#         "email": user.email,
#         "role": user.role
#     }
#
#
#
#
# def handle_google(code):
#     token_data = {
#         "code": code,
#         "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#         "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
#         "redirect_uri": "http://localhost:8080/oauth/google/callback",
#         "grant_type": "authorization_code"
#     }
#     r = requests.post("https://oauth2.googleapis.com/token", data=token_data)
#     if not r.ok:
#         print("Google token error:", r.text)
#         return None
#
#     id_token = r.json().get("id_token")
#     info = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
#     if not info.ok:
#         print("Google ID token error:", info.text)
#         return None
#
#     user_data = info.json()
#     print("Google user data:", user_data)
#     return {
#         "email": user_data.get("email"),
#         "name": user_data.get("name")
#     }
#
# # def handle_github(code):
# #     token_res = requests.post("https://github.com/login/oauth/access_token", data={
# #         "client_id": os.getenv("GITHUB_CLIENT_ID"),
# #         "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
# #         "code": code,
# #         "redirect_uri": "http://localhost:8080/oauth/github/callback"
# #     }, headers={"Accept": "application/json"})
# #
# #     if not token_res.ok:
# #         print("GitHub token error:", token_res.text)
# #         return None
# #
# #     access_token = token_res.json().get("access_token")
# #     if not access_token:
# #         print("GitHub access token missing:", token_res.json())
# #         return None
# #
# #     headers = {"Authorization": f"token {access_token}"}
# #
# #     user_resp = requests.get("https://api.github.com/user", headers=headers)
# #     if not user_resp.ok:
# #         print("GitHub /user error:", user_resp.text)
# #         return None
# #
# #     email_resp = requests.get("https://api.github.com/user/emails", headers=headers)
# #     if not email_resp.ok:
# #         print("GitHub /emails error:", email_resp.text)
# #         return None
# #
# #     user = user_resp.json()
# #     emails = email_resp.json()
# #
# #     print("GitHub user:", user)
# #     print("GitHub emails:", emails)
# #
# #     primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
# #     if not primary_email:
# #         print("No primary verified email found.")
# #         return None
# #
# #     return {
# #         "email": primary_email,
# #         "name": user.get("login")
# #     }
#
#
# def handle_microsoft(code, code_verifier=None):
#     data = {
#         "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
#         "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
#         "code": code,
#         "redirect_uri": "http://localhost:8080/oauth/microsoft/callback",
#         "grant_type": "authorization_code",
#         "code_verifier": code_verifier
#     }
#     #
#     # if code_verifier:
#     #     data["code_verifier"] = code_verifier
#     # else:
#     #     data["client_secret"] = os.getenv("MICROSOFT_CLIENT_SECRET")
#
#     r = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data)
#     if not r.ok:
#         print("Microsoft token error:", r.text)
#         return None
#
#     access_token = r.json().get("access_token")
#     if not access_token:
#         print("Microsoft access token missing")
#         return None
#
#     me = requests.get("https://graph.microsoft.com/v1.0/me", headers={
#         "Authorization": f"Bearer {access_token}"
#     })
#     if not me.ok:
#         print("Microsoft /me error:", me.text)
#         return None
#
#     user_data = me.json()
#     print("Microsoft user data:", user_data)
#
#     return {
#         "email": user_data.get("mail") or user_data.get("userPrincipalName"),
#         "name": user_data.get("displayName")
#     }





import os, requests
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from db.database import SessionLocal
from db.models import User
from utils.utils import create_session_token
from sqlalchemy import create_engine
from db.models import Base
from db.database import engine

Base.metadata.create_all(bind=engine)


load_dotenv()
router = APIRouter()
COOKIE_NAME = "session_token"

# ✅ Input model with optional code_verifier for Microsoft PKCE
class OAuthRequest(BaseModel):
    provider: str
    code: str
    code_verifier: str | None = None

# ✅ Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/oauth")
def oauth_login(payload: OAuthRequest, response: Response, db: Session = Depends(get_db)):
    provider = payload.provider.lower()
    code = payload.code
    code_verifier = payload.code_verifier

    if provider not in ["google", "github", "microsoft"]:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Get user info from the respective provider
    if provider == "google":
        user_info = handle_google(code)
    elif provider == "github":
        user_info = handle_github(code)
    elif provider == "microsoft":
        user_info = handle_microsoft(code, code_verifier)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not available from provider")

    username = user_info.get("name") or email.split("@")[0]

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, username=username, provider=provider, role="user")
            db.add(user)
            db.commit()
            db.refresh(user)
    except Exception as e:
        print("Database error:", e)
        raise HTTPException(status_code=500, detail="Database error")

    session_token = create_session_token(user.email, user.role)
    response.set_cookie(key=COOKIE_NAME, value=session_token, httponly=True   ,secure=True,samesite="None")

    return {
        "message": f"Login via {provider} successful",
        "email": user.email,
        "role": user.role
    }

# ---------------------------
# Google OAuth Handler
# ---------------------------
def handle_google(code):
    token_data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "http://localhost:8080/oauth/google/callback",
        "grant_type": "authorization_code"
    }
    r = requests.post("https://oauth2.googleapis.com/token", data=token_data)
    if not r.ok:
        print("Google token error:", r.text)
        return None

    id_token = r.json().get("id_token")
    info = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
    if not info.ok:
        print("Google ID token error:", info.text)
        return None

    user_data = info.json()
    print("Google user data:", user_data)
    return {
        "email": user_data.get("email"),
        "name": user_data.get("name")
    }

# ---------------------------
# Microsoft OAuth Handler
# ---------------------------
def handle_microsoft(code, code_verifier=None):
    data = {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
        "code": code,
        "redirect_uri": "http://localhost:8080/oauth/microsoft/callback",
        "grant_type": "authorization_code"
    }

    if code_verifier:
        data["code_verifier"] = code_verifier
    else:
        data["client_secret"] = os.getenv("MICROSOFT_CLIENT_SECRET")

    r = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data)
    if not r.ok:
        print("Microsoft token error:", r.text)
        return None

    access_token = r.json().get("access_token")
    if not access_token:
        print("Microsoft access token missing")
        return None

    me = requests.get("https://graph.microsoft.com/v1.0/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    if not me.ok:
        print("Microsoft /me error:", me.text)
        return None

    user_data = me.json()
    print("Microsoft user data:", user_data)

    return {
        "email": user_data.get("mail") or user_data.get("userPrincipalName"),
        "name": user_data.get("displayName")
    }

# ---------------------------
# GitHub OAuth Handler (Optional)
# ---------------------------
# def handle_github(code):
#     token_res = requests.post("https://github.com/login/oauth/access_token", data={
#         "client_id": os.getenv("GITHUB_CLIENT_ID"),
#         "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
#         "code": code,
#         "redirect_uri": "http://localhost:8080/oauth/github/callback"
#     }, headers={"Accept": "application/json"})
#
#     if not token_res.ok:
#         print("GitHub token error:", token_res.text)
#         return None
#
#     access_token = token_res.json().get("access_token")
#     if not access_token:
#         print("GitHub access token missing:", token_res.json())
#         return None
#
#     headers = {"Authorization": f"token {access_token}"}
#
#     user_resp = requests.get("https://api.github.com/user", headers=headers)
#     if not user_resp.ok:
#         print("GitHub /user error:", user_resp.text)
#         return None
#
#     email_resp = requests.get("https://api.github.com/user/emails", headers=headers)
#     if not email_resp.ok:
#         print("GitHub /emails error:", email_resp.text)
#         return None
#
#     user = user_resp.json()
#     emails = email_resp.json()
#
#     primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
#     if not primary_email:
#         print("No primary verified email found.")
#         return None
#
#     return {
#         "email": primary_email,
#         "name": user.get("login")
#     }
