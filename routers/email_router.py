# # # routers/email_router.py
# # from fastapi import APIRouter, Depends, HTTPException
# # from pydantic import BaseModel
# # from uuid import uuid4
# # from sqlalchemy.orm import Session
# # import imaplib, smtplib
# # from datetime import datetime
# #
# # from db.database import get_db
# # from db.models import EmailConnection, EmailSyncSettings
# # from services.crypto_utils import encrypt_password, decrypt_password
# # from services.email_service import process_email_account
# # from db.models import Base
# # from db.database import engine
# #
# # Base.metadata.create_all(bind=engine)
# #
# #
# # router = APIRouter()
# #
# # class ConnectPayload(BaseModel):
# #     email: str
# #     password: str
# #     user_id: str  # ✅ Add this line
# #     imap: dict
# #     smtp: dict
# #
# #
# # class SyncPayload(BaseModel):
# #     email_id: str; auto_sync: bool; email_folders: list[str]; email_documents: list[str]; sync_interval: int
# #
# # @router.post("/api/email/connect")
# # def api_connect(payload: ConnectPayload, db: Session = Depends(get_db)):
# #     # Validate IMAP/SMTP
# #     try:
# #         imap = (imaplib.IMAP4_SSL if payload.imap.get("use_ssl", True) else imaplib.IMAP4)(
# #             payload.imap["host"], payload.imap["port"])
# #         imap.login(payload.email, payload.password); imap.logout()
# #         smtp = (smtplib.SMTP_SSL if payload.smtp.get("use_ssl", True) else smtplib.SMTP)(
# #             payload.smtp["host"], payload.smtp["port"])
# #         smtp.login(payload.email, payload.password); smtp.quit()
# #     except Exception as e:
# #         raise HTTPException(400, detail=f"Connection failed: {e}")
# #
# #     conn_id = uuid4()
# #     db.add(EmailConnection(
# #         id=conn_id, user_id=payload.user_id, email=payload.email,
# #         password=encrypt_password(payload.password),
# #         status="connected",
# #         imap_config=payload.imap, smtp_config=payload.smtp))
# #     db.commit()
# #     return {"status": "connected", "email": payload.email, "provider": "custom", "email_id": str(conn_id)}
# #
# # @router.post("/api/sync/email")
# # def api_sync(payload: SyncPayload, db: Session = Depends(get_db)):
# #     db.merge(EmailSyncSettings(
# #         email_id=payload.email_id, auto_sync=payload.auto_sync,
# #         email_folders=payload.email_folders, email_documents=payload.email_documents,
# #         sync_interval=payload.sync_interval))
# #     db.commit()
# #     return {"message": "Sync settings saved", "sync_details": {"auto_sync": payload.auto_sync, "folders": payload.email_folders, "interval": payload.sync_interval}}
# #
# # @router.post("/api/sync/run/{email_id}")
# # def run_sync(email_id: str, db: Session = Depends(get_db)):
# #     conn = db.query(EmailConnection).filter_by(id=email_id).first()
# #     sync = db.query(EmailSyncSettings).filter_by(email_id=email_id).first()
# #     if not conn or not sync:
# #         raise HTTPException(404, detail="Missing connection or settings")
# #     if not sync.auto_sync:
# #         raise HTTPException(400, detail="Auto-sync disabled")
# #
# #     conn.status = "syncing"; db.commit()
# #     result = process_email_account(email_id, "output", "temp", "hashes.txt", None)
# #     sync.last_sync = datetime.utcnow(); conn.status = "connected"; db.commit()
# #     return result
# #
# # @router.get("/api/email/user/{user_id}")
# # def get_emails_by_user(user_id: str, db: Session = Depends(get_db)):
# #     connections = db.query(EmailConnection).filter_by(user_id=user_id).all()
# #     settings_map = {
# #         s.email_id: s for s in db.query(EmailSyncSettings).filter(
# #             EmailSyncSettings.email_id.in_([c.id for c in connections])
# #         )
# #     }
# #
# #     response = []
# #     for conn in connections:
# #         sync = settings_map.get(conn.id)
# #         response.append({
# #             "provider": "custom",
# #             "email": conn.email,
# #             "user_id": conn.user_id,
# #             "status": conn.status,
# #             "email_id": conn.id,
# #             "lastSync": sync.last_sync if sync else None,
# #             "syncInterval": sync.sync_interval if sync else None,
# #             "enabledFolders": sync.email_folders if sync else [],
# #             "enabledDocuments": sync.email_documents if sync else [],
# #             "autoSync": sync.auto_sync if sync else False
# #         })
# #
# #     return response
#
#
#
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from uuid import uuid4
# from sqlalchemy.orm import Session
# from datetime import datetime
# import imaplib
# import smtplib
# from enum import Enum
#
# from db.database import get_db
# from db.models import EmailConnection, EmailSyncSettings
# from services.crypto_utils import encrypt_password, decrypt_password
# from services.email_service import process_email_account
# from db.models import Base
# from db.database import engine
# from core.custom_exception import CustomAPIException
#
# # Base.metadata.create_all(bind=engine)
#
# router = APIRouter()
#
#
# # ----------------------
# # ENUM for connection status
# # ----------------------
# class ConnectionStatus(str, Enum):
#     CONNECTED = "connected"
#     DISCONNECTED = "disconnected"
#     SYNCING = "syncing"
#     FAILED = "failed"
#
#
# # ----------------------
# # Payload Schemas
# # ----------------------
# class ConnectPayload(BaseModel):
#     email: str
#     password: str
#     user_id: str
#     imap: dict
#     smtp: dict
#
#
# class SyncPayload(BaseModel):
#     email: str
#     auto_sync: bool
#     email_folders: list[str]
#     email_documents: list[str]
#     sync_interval: int
#
#
# # ----------------------
# # Connect to Email (IMAP/SMTP validation)
# # ----------------------
# @router.post("/api/email/connect")
# def api_connect(payload: ConnectPayload, db: Session = Depends(get_db)):
#     try:
#         imap_cls = imaplib.IMAP4_SSL if payload.imap.get("use_ssl", True) else imaplib.IMAP4
#         imap = imap_cls(payload.imap["host"], payload.imap["port"])
#         imap.login(payload.email, payload.password)
#         imap.logout()
#
#         smtp_cls = smtplib.SMTP_SSL if payload.smtp.get("use_ssl", True) else smtplib.SMTP
#         smtp = smtp_cls(payload.smtp["host"], payload.smtp["port"])
#         smtp.login(payload.email, payload.password)
#         smtp.quit()
#     except Exception as e:
#         raise CustomAPIException("E_EMAIL_CONN", "Failed to connect to email server", 400, {"error": str(e)})
#
#     conn_id = uuid4()
#     db.add(EmailConnection(
#         id=conn_id,
#         user_id=payload.user_id,
#         email=payload.email,
#         password=encrypt_password(payload.password),
#         status=ConnectionStatus.CONNECTED,
#         imap_config=payload.imap,
#         smtp_config=payload.smtp
#     ))
#     db.commit()
#
#     return {"success": True, "email": payload.email, "email_id": str(conn_id), "provider": "custom"}
#
#
# # ----------------------
# # Save Sync Settings
# # ----------------------
# @router.post("/api/sync/email")
# def api_sync(payload: SyncPayload, db: Session = Depends(get_db)):
#     db.merge(EmailSyncSettings(
#         email=payload.email,
#         auto_sync=payload.auto_sync,
#         email_folders=payload.email_folders,
#         email_documents=payload.email_documents,
#         sync_interval=payload.sync_interval
#     ))
#     db.commit()
#     return {
#         "message": "Sync settings saved",
#         "sync_details": {
#             "auto_sync": payload.auto_sync,
#             "folders": payload.email_folders,
#             "interval": payload.sync_interval
#         }
#     }
#
#
# # @router.post("/api/sync/email")
# # def api_sync(payload: SyncPayload, db: Session = Depends(get_db)):
# #     db.merge(EmailSyncSettings(
# #         email=payload.email, auto_sync=payload.auto_sync,
# #         email_folders=payload.email_folders, email_documents=payload.email_documents,
# #         sync_interval=payload.sync_interval))
# #     db.commit()
# #     return {"message": "Sync settings saved", "sync_details": {"auto_sync": payload.auto_sync, "folders": payload.email_folders, "interval": payload.sync_interval}}
# #
#
# # ----------------------
# # Run Sync Immediately
# # ----------------------
# @router.post("/api/sync/run/{email}")
# def run_sync(email: str, db: Session = Depends(get_db)):
#     conn = db.query(EmailConnection).filter_by(email=email).first()
#     sync = db.query(EmailSyncSettings).filter_by(email=email).first()
#
#     if not conn or not sync:
#         raise HTTPException(404, detail="Missing connection or settings")
#
#     if not sync.auto_sync:
#         raise HTTPException(400, detail="Auto-sync disabled")
#
#     conn.status = ConnectionStatus.SYNCING
#     db.commit()
#
#     result = process_email_account(email, "/home/yavar/3-way-mapping/app/data_store/raw_store_1", "temp", "hashes.txt", None)
#
#     # Update status and last sync
#     conn.status = ConnectionStatus.CONNECTED
#     sync.last_sync = datetime.utcnow()
#     db.commit()
#
#     return result
#
#
# # ----------------------
# # Get Email Accounts by User
# # ----------------------
# @router.get("/api/email/user/{email}")
# def get_emails_by_user(email: str, db: Session = Depends(get_db)):
#     connections = db.query(EmailConnection).filter_by(email=email).all()
#
#
#     settings_map = {
#         s.email: s for s in db.query(EmailSyncSettings).filter(
#             EmailSyncSettings.email.in_([c.email for c in connections])
#         )
#     }
#
#     response = []
#     for conn in connections:
#         sync = settings_map.get(conn.id)
#         response.append({
#             "provider": "custom",
#             "email": conn.email,
#             "user_id": conn.user_id,
#             "status": conn.status,
#             "email_id": str(conn.id),
#             "lastSync": sync.last_sync if sync else None,
#             "syncInterval": sync.sync_interval if sync else None,
#             "enabledFolders": sync.email_folders if sync else [],
#             "enabledDocuments": sync.email_documents if sync else [],
#             "autoSync": sync.auto_sync if sync else False
#         })
#
#     return response


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import imaplib
import smtplib
from enum import Enum

from db.database import get_db
from db.models import EmailConnection, EmailSyncSettings, User
from services.crypto_utils import encrypt_password
from services.email_service import process_email_account
from core.custom_exception import CustomAPIException
from utils.dependencies import get_current_user  # 👈 Requires session logic (see below)

from sqlalchemy import create_engine
from db.models import Base
from db.database import engine

Base.metadata.create_all(bind=engine)

router = APIRouter()

# ----------------------
# ENUM for connection status
# ----------------------
class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    FAILED = "failed"

# ----------------------
# Payload Schemas
# ----------------------
class ConnectPayload(BaseModel):
    email: str
    password: str
    username: str
    imap: dict
    smtp: dict

class SyncPayload(BaseModel):
    email: str
    auto_sync: bool
    email_folders: list[str]
    email_documents: list[str]
    sync_interval: int

# ----------------------
# Connect to Email (IMAP/SMTP validation)
# ----------------------
@router.post("/api/email/connect")
def api_connect(payload: ConnectPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        imap_cls = imaplib.IMAP4_SSL if payload.imap.get("use_ssl", True) else imaplib.IMAP4
        imap = imap_cls(payload.imap["host"], payload.imap["port"])
        imap.login(payload.email, payload.password)
        imap.logout()

        smtp_cls = smtplib.SMTP_SSL if payload.smtp.get("use_ssl", True) else smtplib.SMTP
        smtp = smtp_cls(payload.smtp["host"], payload.smtp["port"])
        smtp.login(payload.email, payload.password)
        smtp.quit()
    except Exception as e:
        raise CustomAPIException("E_EMAIL_CONN", "Failed to connect to email server", 400, {"error": str(e)})

    conn_id = uuid4()
    db.add(EmailConnection(
        id=conn_id,
        user_email=current_user.email,
        email=payload.email,
        password=encrypt_password(payload.password),
        status=ConnectionStatus.CONNECTED,
        imap_config=payload.imap,
        smtp_config=payload.smtp
    ))
    db.commit()

    return {
        "success": True,
        "email": payload.email,
        "email_id": str(conn_id),
        "provider": "custom"
    }

# ----------------------
# Save Sync Settings
# ----------------------
@router.post("/api/sync/email")
def api_sync(payload: SyncPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conn = db.query(EmailConnection).filter_by(email=payload.email, user_email=current_user.email).first()
    if not conn:
        raise HTTPException(status_code=403, detail="Unauthorized to sync this email")

    db.merge(EmailSyncSettings(
        email=payload.email,
        user
        auto_sync=payload.auto_sync,
        email_folders=payload.email_folders,
        email_documents=payload.email_documents,
        sync_interval=payload.sync_interval
    ))
    db.commit()

    return {
        "message": "Sync settings saved",
        "sync_details": {
            "auto_sync": payload.auto_sync,
            "folders": payload.email_folders,
            "interval": payload.sync_interval
        }
    }

# ----------------------
# Run Sync Immediately
# ----------------------
@router.post("/api/sync/run/{email}")
def run_sync(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conn = db.query(EmailConnection).filter_by(email=email, user_email=current_user.email).first()
    sync = db.query(EmailSyncSettings).filter_by(email=email).first()

    if not conn or not sync:
        raise HTTPException(404, detail="Missing connection or settings")

    if not sync.auto_sync:
        raise HTTPException(400, detail="Auto-sync disabled")

    conn.status = ConnectionStatus.SYNCING
    db.commit()

    result = process_email_account(
        email,
        "/home/yavar/3-way-mapping/app/data_store/raw_store_1",  # You can parameterize this
        "temp",
        "hashes.txt",
        None
    )

    conn.status = ConnectionStatus.CONNECTED
    sync.last_sync = datetime.utcnow()
    db.commit()

    return result





# ----------------------
# Get Email Accounts by User
# ----------------------
@router.get("/api/email/user/{email}")
def get_emails_by_user(email: str, db: Session = Depends(get_db)):
    connections = db.query(EmailConnection).filter_by(email=email).all()


    settings_map = {
        s.email: s for s in db.query(EmailSyncSettings).filter(
            EmailSyncSettings.email.in_([c.email for c in connections])
        )
    }

    response = []
    for conn in connections:
        sync = sync = settings_map.get(conn.email)
        response.append({
            "provider": "custom",
            "email": conn.email,
            "user_id": conn.user_email,
            "status": conn.status,
            "lastSync": sync.last_sync if sync else None,
            "syncInterval": sync.sync_interval if sync else None,
            "enabledFolders": sync.email_folders if sync else [],
            "enabledDocuments": sync.email_documents if sync else [],
            "autoSync": sync.auto_sync if sync else False
        })

    return response




# ----------------------
# Get All Emails Linked to Logged-in User
# ----------------------
@router.get("/api/email/user")
def get_emails_by_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    connections = db.query(EmailConnection).filter_by(user_email=current_user.email).all()
    settings_map = {
        s.email: s for s in db.query(EmailSyncSettings).filter(
            EmailSyncSettings.email.in_([c.email for c in connections])
        )
    }

    return [{
        "provider": "custom",
        "email": conn.email,
        "user_id": conn.user_email,
        "status": conn.status,
        "email_id": str(conn.id),
        "lastSync": settings_map[conn.email].last_sync if conn.email in settings_map else None,
        "syncInterval": settings_map[conn.email].sync_interval if conn.email in settings_map else None,
        "enabledFolders": settings_map[conn.email].email_folders if conn.email in settings_map else [],
        "enabledDocuments": settings_map[conn.email].email_documents if conn.email in settings_map else [],
        "autoSync": settings_map[conn.email].auto_sync if conn.email in settings_map else False
    } for conn in connections]
