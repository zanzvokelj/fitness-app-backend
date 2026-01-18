import os
import requests

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

RESEND_URL = "https://api.resend.com/emails"


def send_email(
    *,
    to_email: str,
    subject: str,
    html_body: str,
) -> None:
    if not RESEND_API_KEY or not EMAIL_FROM:
        print("Resend not configured, skipping email")
        return

    try:
        response = requests.post(
            RESEND_URL,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": EMAIL_FROM,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            },
            timeout=10,
        )

        if response.status_code >= 400:
            print("Resend error:", response.text)

    except Exception as e:
        print("Resend exception:", e)