import os
from typing import Optional
import requests
from dotenv import load_dotenv
from db.database import get_db
from db.models import EmailConnection, EmailSyncSettings, User
from sqlalchemy.orm import Session

# Load all environment variables from `.env` file
load_dotenv()

# def handle_microsoft(code: str, verifier: Optional[str] = None):
#     client_id = os.getenv("MICROSOFT_CLIENT_ID")
#     client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
#     redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI")
#
#     print("📢 MICROSOFT_CLIENT_ID:", client_id)  # Optional debug
#     if not client_id:
#         print("❌ Microsoft client_id missing from environment!")
#         return None
#
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "code": code,
#         "redirect_uri": redirect_uri,
#         "grant_type": "authorization_code",
#         "scope": "https://graph.microsoft.com/User.Read openid email profile",
#         "code_verifier": verifier,
#     }
#
#     # if verifier:
#     #     data["code_verifier"] = verifier
#
#     token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
#     resp = requests.post(token_url, data=data)
#
#     try:
#         token_data = resp.json()
#     except Exception as e:
#         print("❌ Failed to parse Microsoft token JSON:", e)
#         return None
#
#     print("🔄 Microsoft token response:", token_data)
#
#     access_token = token_data.get("access_token")
#     if not access_token:
#         print("❌ Microsoft access token missing")
#         return None
#
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#
#     user_info_url = "https://graph.microsoft.com/v1.0/me"
#     user_resp = requests.get(user_info_url, headers=headers)
#
#     try:
#         user_data = user_resp.json()
#         print("👤 Microsoft user info:", user_data)
#         return user_data if user_resp.ok else None
#     except Exception as e:
#         print("❌ Failed to parse Microsoft user info JSON:", e)
#         return None




def handle_microsoft(code: str, verifier: Optional[str] = None):
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
    redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI")

    print("📢 MICROSOFT_CLIENT_ID:", client_id)
    if not client_id:
        print("❌ Microsoft client_id missing from environment!")
        return None

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    if verifier:
        data["code_verifier"] = verifier

    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    resp = requests.post(token_url, data=data)

    try:
        token_data = resp.json()
        if "error" in token_data:
            print("🔄 Microsoft token response:", token_data)
            return None
        return token_data
    except Exception as e:
        print("❌ Failed to parse Microsoft token JSON:", e)
        return None


def handle_google(code: str):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    print("📢 GOOGLE_CLIENT_ID:", client_id)  # Optional debug
    if not client_id:
        print("❌ Google client_id missing from environment!")
        return None

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    resp = requests.post(token_url, data=data)

    if not resp.ok:
        print("❌ Google token fetch failed:", resp.text)
        return None

    id_token = resp.json().get("id_token")
    if not id_token:
        print("❌ No ID token returned from Google")
        return None

    info = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
    return info.json() if info.ok else None



def refresh_google_token(conn: EmailConnection):
    token_url = "https://oauth2.googleapis.com/token"
    resp = requests.post(token_url, data={
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": conn.refresh_token,
        "grant_type": "refresh_token"
    })
    data = resp.json()
    if resp.ok and "access_token" in data:
        conn.access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        conn.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        return True
    return False


def refresh_microsoft_token(conn: EmailConnection):
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    resp = requests.post(token_url, data={
        "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
        "refresh_token": conn.refresh_token,
        "grant_type": "refresh_token",
        "scope": "https://graph.microsoft.com/User.Read offline_access"
    })
    data = resp.json()
    if resp.ok and "access_token" in data:
        conn.access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        conn.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        return True
    return False


def validate_and_refresh_token(conn: EmailConnection, db: Session):
    if conn.connection_type == "oauth" and conn.token_expiry and conn.token_expiry <= datetime.utcnow():
        if conn.provider == "gmail" and refresh_google_token(conn):
            db.commit()
        elif conn.provider == "outlook" and refresh_microsoft_token(conn):
            db.commit()
        else:
            raise HTTPException(401, "OAuth token expired and refresh failed")



