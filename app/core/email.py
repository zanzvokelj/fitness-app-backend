# app/core/email.py

import os
import smtplib
from pathlib import Path
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =======================
# SMTP CONFIG
# =======================

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM]):
    raise RuntimeError("SMTP configuration is incomplete")

# =======================
# EMAIL SENDER
# =======================

def send_email(
    *,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = to_email

    if text_body:
        message.attach(MIMEText(text_body, "plain"))

    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(
                from_addr=SMTP_USER,
                to_addrs=[to_email],
                msg=message.as_string(),
            )
    except Exception as exc:
        raise RuntimeError("Failed to send email") from exc


# =======================
# TEMPLATE RENDERING
# =======================

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"

def render_template(template_name: str, **context) -> str:
    template_path = TEMPLATES_DIR / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Email template not found: {template_name}")

    html = template_path.read_text(encoding="utf-8")

    for key, value in context.items():
        html = html.replace(f"{{{{ {key} }}}}", str(value))

    return html