import os
import email
import imaplib
from datetime import datetime
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime

from db.models import EmailConnection, EmailSyncSettings, EmailRecord
from db.database import SessionLocal
from services.crypto_utils import decrypt_password  # Optional, if using encryption
from .utils import ensure_dirs, hash_file
from .pdf_processor import PDFProcessor


def decode_mime(text):
    try:
        return str(make_header(decode_header(text)))
    except Exception:
        return text or ""


def connect_imap(imap_cfg, email_user, email_pass):
    cls = imaplib.IMAP4_SSL if imap_cfg.get("use_ssl", True) else imaplib.IMAP4
    conn = cls(imap_cfg["host"], imap_cfg["port"])
    conn.login(email_user, email_pass)
    return conn


def is_duplicate(pdf_hash, hash_path):
    if not os.path.exists(hash_path):
        return False
    with open(hash_path, 'r') as f:
        return any(pdf_hash == line.strip() for line in f)


def save_hash(pdf_hash, hash_path):
    with open(hash_path, 'a') as f:
        f.write(pdf_hash + "\n")


def process_email_account(email_id: str, save_dir: str, temp_dir: str, hash_path: str, email_pass: str = None):
    db = SessionLocal()
    try:
        conn_info = db.query(EmailConnection).filter_by(email=email_id).first()
        sync_cfg = db.query(EmailSyncSettings).filter_by(email=email_id).first()

        if not conn_info or not sync_cfg:
            raise ValueError("Email connection or sync configuration not found.")

        # Use encrypted password if applicable
        password = email_pass or conn_info.password
        if not password:
            raise ValueError("Missing email password")

        # Decrypt password if encrypted
        if conn_info.password.startswith("gAAAA"):  # indicative of Fernet token
            from services.crypto_utils import decrypt_password
            password = decrypt_password(password)

        conn = connect_imap(conn_info.imap_config, conn_info.email, password)
        pdf = PDFProcessor(temp_dir)

        ensure_dirs(save_dir, temp_dir)
        processed = 0

        for folder in sync_cfg.email_folders:
            conn.select(folder)
            status, data = conn.search(None, "UNSEEN")
            if status != "OK":
                continue

            for eid in data[0].split():
                status, mdata = conn.fetch(eid, "(RFC822)")
                if status != "OK":
                    continue

                msg = email.message_from_bytes(mdata[0][1])

                sender = decode_mime(msg.get("From", ""))
                subject = decode_mime(msg.get("Subject", ""))
                try:
                    dt = parsedate_to_datetime(msg.get("Date")).astimezone()
                except Exception:
                    dt = datetime.now()
                received_time = dt.strftime("%Y-%m-%d %H:%M:%S")

                pdf_parts = [
                    part for part in msg.walk()
                    if part.get_content_maintype() != "multipart"
                    and part.get("Content-Disposition")
                    and part.get_filename()
                    and part.get_filename().lower().endswith(tuple(sync_cfg.email_documents))
                ]

                for ai, part in enumerate(pdf_parts, 1):
                    filename = decode_mime(part.get_filename())
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    temp_pdf_path = os.path.join(temp_dir, f"{timestamp}_{filename}")

                    with open(temp_pdf_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))

                    file_hash = hash_file(temp_pdf_path)
                    if is_duplicate(file_hash, hash_path):
                        os.remove(temp_pdf_path)
                        continue

                    save_hash(file_hash, hash_path)

                    # Convert PDF to images
                    images = pdf.convert_to_images(temp_pdf_path, os.path.splitext(filename)[0])
                    for pi, img_path in enumerate(images, 1):
                        final_path = os.path.join(save_dir, os.path.basename(img_path))
                        os.rename(img_path, final_path)

                        record = EmailRecord(
                            email_uid=eid.decode(),
                            original_attachment_name=filename,
                            attachment_file_name=os.path.basename(final_path),
                            sender_id_name=sender,
                            received_date_time=received_time,
                            subject=f"{subject} (Attachment {ai}, Page {pi})",
                            attachment_path=final_path,
                            attachment_num_total=len(images),
                        )
                        db.add(record)

                    db.commit()
                    os.remove(temp_pdf_path)
                    processed += 1

                conn.store(eid, '+FLAGS', '\\Seen')

        conn.logout()
        return {"processed": processed}

    finally:
        db.close()
