# app/core/email.py
import os
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_email(*, to_email: str, subject: str, html_body: str) -> None:
    # ✅ CHECK ŠELE TUKAJ
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM]):
        print("SMTP not configured, skipping email")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], message.as_string())


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"

def render_template(template_name: str, **context) -> str:
    html = (TEMPLATES_DIR / template_name).read_text(encoding="utf-8")
    for k, v in context.items():
        html = html.replace(f"{{{{ {k} }}}}", str(v))
    return html