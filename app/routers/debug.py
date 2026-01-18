from fastapi import APIRouter

from app.core.email_resend import send_email
from app.main import app

router = APIRouter(tags=["debug"])



@app.get("/test-email")
def test_email():
    send_email(
        to_email="zan.fitness.app@gmail.com",
        subject="Resend test ✅",
        html_body="<h1>Email works!</h1>",
    )
    return {"ok": True}