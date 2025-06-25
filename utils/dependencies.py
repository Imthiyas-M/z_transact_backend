from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from utils.utils import verify_session_token

COOKIE_NAME = "session_token"

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_token = request.cookies.get(COOKIE_NAME)
    print(session_token)

    if not session_token:
        raise HTTPException(status_code=401, detail="Session token missing")

    payload = verify_session_token(session_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
