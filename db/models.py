# import uuid
# import enum
# from sqlalchemy import (
#     Column, String, Enum as SqlEnum, JSON, Boolean, Integer,
#     DateTime, ForeignKey  # ✅ Added ForeignKey, Boolean, Integer, DateTime
# )
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()
#
# class ConnectionStatus(str, enum.Enum):
#     CONNECTED = "connected"
#     DISCONNECTED = "disconnected"
#     SYNCING = "syncing"
#     FAILED = "failed"
#
# class EmailConnection(Base):
#     __tablename__ = "email_connections"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(String, nullable=False,unique=True)
#     email = Column(String, nullable=False,unique=True)
#     password = Column(String, nullable=False)
#     status = Column(SqlEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.DISCONNECTED)
#     imap_config = Column(JSON, nullable=True)
#     smtp_config = Column(JSON, nullable=True)
#
#
# class EmailSyncSettings(Base):
#     __tablename__ = "email_sync_settings"
#     id = Column(UUID(as_uuid=True),  default=uuid.uuid4)
#     email = Column(String, ForeignKey("email_connections.email"),primary_key=True)
#     auto_sync = Column(Boolean, default=False)
#     email_folders = Column(JSON, default=list)
#     email_documents = Column(JSON, default=list)
#     sync_interval = Column(Integer, default=15)
#     last_sync = Column(DateTime, nullable=True)
#
# class EmailRecord(Base):
#     __tablename__ = "email_records"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     email_uid = Column(String, nullable=False)
#     original_attachment_name = Column(String)
#     attachment_file_name = Column(String)
#     sender_id_name = Column(String)
#     received_date_time = Column(String)
#     subject = Column(String)
#     attachment_path = Column(String)
#     attachment_num_total = Column(Integer)
#     doc_type = Column(String, default="Unclassified")
#
#
#
# class User(Base):
#     __tablename__ = 'users'
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     username = Column(String, index=True, nullable=False)
#     role = Column(String, default="user")
#     hashed_password = Column(String, nullable=True)
#     provider = Column(String, default="local")  # 'google' or 'local'
#     reset_token = Column(String, nullable=True)



"""
this older version - 25/06/25
"""


#
#
# import uuid, enum
# from datetime import datetime
# from sqlalchemy import (
#     Column, String, Enum as SqlEnum, JSON, Boolean, Integer,
#     DateTime, ForeignKey, Index, UniqueConstraint
# )
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
#
# Base = declarative_base()
#
# class ConnectionStatus(str, enum.Enum):
#     CONNECTED = "connected"
#     DISCONNECTED = "disconnected"
#     SYNCING = "syncing"
#     FAILED = "failed"
#
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     username = Column(String, index=True, nullable=False)
#     role = Column(String, default="user")
#     hashed_password = Column(String, nullable=True)
#     provider = Column(String, default="local")
#     reset_token = Column(String, nullable=True)
#     connections = relationship("EmailConnection", back_populates="user", cascade="all, delete-orphan")
#
# class EmailConnection(Base):
#     __tablename__ = "email_connections"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), unique=True, index=True, nullable=False)
#     email = Column(String, nullable=False)
#     provider = Column(String, default="custom")
#     connection_type = Column(String, default="imap")
#     password = Column(String, nullable=True)
#     imap_config = Column(JSON, nullable=True)
#     smtp_config = Column(JSON, nullable=True)
#     access_token = Column(String, nullable=True)
#     refresh_token = Column(String, nullable=True)
#     token_expiry = Column(DateTime, nullable=True)
#     status = Column(SqlEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.DISCONNECTED)
#     user = relationship("User", back_populates="connections")
#     sync_settings = relationship("EmailSyncSettings", back_populates="connection", cascade="all, delete-orphan", uselist=False)
#     records = relationship("EmailRecord", back_populates="connection", cascade="all, delete-orphan")
#     __table_args__ = (
#         UniqueConstraint("email", "user_email", name="uq_user_email_combo"),
#         Index("ix_email_connections_user_email", "user_email"),
#         Index("ix_email_connections_email", "email"),
#     )
#
# class EmailSyncSettings(Base):
#     __tablename__ = "email_sync_settings"
#
#     email = Column(String, ForeignKey("email_connections.email", ondelete="CASCADE"), nullable=False,primary_key=True)
#     auto_sync = Column(Boolean, default=False)
#     email_folders = Column(JSON, default=list)
#     email_documents = Column(JSON, default=list)
#     sync_interval = Column(Integer, default=15)
#     last_sync = Column(DateTime, nullable=True)
#     connection = relationship("EmailConnection", back_populates="sync_settings")
#
# class EmailRecord(Base):
#     __tablename__ = "email_records"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     email = Column(String, ForeignKey("email_connections.email", ondelete="CASCADE"), nullable=False)
#     email_uid = Column(String, nullable=False)
#     original_attachment_name = Column(String)
#     attachment_file_name = Column(String)
#     sender_id_name = Column(String)
#     received_date_time = Column(DateTime, default=datetime.utcnow)
#     subject = Column(String)
#     attachment_path = Column(String)
#     attachment_num_total = Column(Integer, default=0)
#     doc_type = Column(String, default="Unclassified")
#     connection = relationship("EmailConnection", back_populates="records")



import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Enum as SqlEnum, JSON, Boolean, Integer,
    DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# --- ENUMS ---
class ConnectionStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    FAILED = "failed"

# --- USER TABLE ---
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    role = Column(String, default="user")
    hashed_password = Column(String, nullable=True)
    provider = Column(String, default="local")  # local / google / outlook
    reset_token = Column(String, nullable=True)

    connections = relationship("EmailConnection", back_populates="user", cascade="all, delete-orphan")

# --- EMAIL CONNECTION ---
class EmailConnection(Base):
    __tablename__ = "email_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)
    provider = Column(String, default="custom")  # custom / gmail / outlook
    connection_type = Column(String, default="imap")  # imap / smtp / oauth

    password = Column(String, nullable=True)
    imap_config = Column(JSON, nullable=True)
    smtp_config = Column(JSON, nullable=True)

    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    status = Column(SqlEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.DISCONNECTED)

    user = relationship("User", back_populates="connections")
    sync_settings = relationship("EmailSyncSettings", back_populates="connection", cascade="all, delete-orphan", uselist=False)
    records = relationship("EmailRecord", back_populates="connection", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("email", "user_email", name="uq_user_email_combo"),
        Index("ix_email_connections_user_email", "user_email"),
        Index("ix_email_connections_email", "email"),
    )

# --- SYNC SETTINGS ---
class EmailSyncSettings(Base):
    __tablename__ = "email_sync_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("email_connections.id", ondelete="CASCADE"), nullable=False, unique=True)

    auto_sync = Column(Boolean, default=False)
    email_folders = Column(JSON, default=list)
    email_documents = Column(JSON, default=list)
    sync_interval = Column(Integer, default=15)
    last_sync = Column(DateTime, nullable=True)

    connection = relationship("EmailConnection", back_populates="sync_settings")

# --- EMAIL RECORD (Modified) ---
class EmailRecord(Base):
    __tablename__ = "email_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("email_connections.id", ondelete="CASCADE"), nullable=False)

    email_uid = Column(String, nullable=False)
    file_name = Column(String)
    file_path = Column(String)
    sender_id_name = Column(String)
    received_date_time = Column(DateTime, default=datetime.utcnow)
    subject = Column(String)
    doc_type = Column(String, default="Unclassified")

    connection = relationship("EmailConnection", back_populates="records")
