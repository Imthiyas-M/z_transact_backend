import imaplib

EMAIL = "billdeskyavartst@gmail.com"
PASSWORD = "ceth bkyl hboi uurq"  # App password

try:
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(EMAIL, PASSWORD)
    print("✅ Login successful")
except Exception as e:
    print("❌ Login failed:", e)
