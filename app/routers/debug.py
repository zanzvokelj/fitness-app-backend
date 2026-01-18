from fastapi import APIRouter
from app.core.email import send_email

router = APIRouter(tags=["debug"])

@router.get("/test-email")
def test_email():
    send_email(
        to_email="zan.fitness.app@gmail.com",  # ← tvoj email
        subject="SMTP TEST ✅",
        html_body="<h1>Hello SMTP</h1><p>If you see this, email works.</p>",
    )
    return {"ok": True}