# app/services/ai_chat.py
from sqlalchemy.orm import Session
from app.services.schedule_service import get_weekly_schedule_text
from openai import OpenAI
from typing import List, Dict

from app.core.config import settings

# -------------------------------------------------
# OpenAI client
# -------------------------------------------------
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# -------------------------------------------------
# System prompt (VERY IMPORTANT)
# -------------------------------------------------
def build_system_prompt(schedule_text: str) -> str:
    return f"""
Si AI fitnes svetovalec znotraj aplikacije fitnes centra.

POMEMBNA PRAVILA (BREZ IZJEM):
- Svetuješ IZKLJUČNO glede skupinskih vadb
- Na voljo imaš SAMO spodnji urnik
- Ne izmišljuješ terminov, vadb ali urnikov
- Ne predlagaš teka, vaj doma ali individualnih treningov
- Ne sprašuješ po imenu fitnes centra
- Predpostaviš, da je uporabnik že v aplikaciji
- Urnik je enak vsak teden

TEDENSKI URNIK SKUPINSKIH VADB:
{schedule_text}

TVOJA NALOGA:
- pomagaj uporabniku izbrati primerne skupinske vadbe
- pojasni, katere vadbe so primerne za njegov cilj
- če želi razpored, predlagaj KONKRETNE dneve in ure iz urnika
- odgovarjaj kratko, jasno in prijazno
- uporabljaj slovenščino
"""

# -------------------------------------------------
# Chat function
# -------------------------------------------------
def chat_with_ai(db: Session, messages: list[dict]) -> str:
    schedule_text = get_weekly_schedule_text(db)
    system_prompt = build_system_prompt(schedule_text)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        temperature=0.3,  # zelo pomembno
        max_tokens=300,
    )
    return response.choices[0].message.content
