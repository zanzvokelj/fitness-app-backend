# app/services/ai_chat.py

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
SYSTEM_PROMPT = """
Si AI fitnes svetovalec za skupinske vadbe v fitnes centru.

POMEMBNA PRAVILA:
- Svetuješ IZKLJUČNO glede skupinskih vadb (BodyPump, Core, Kickbox, BodyBalance)
- NE predlagaš teka, uteži, vaj doma ali individualnih treningov
- NE izmišljuješ vadb, terminov ali cen
- Uporabljaš samo obstoječe tipe skupinskih vadb
- Uporabljaš slovenščino
- Odgovarjaš jasno, kratko in prijazno

Tvoja naloga:
- pomagaj uporabniku izbrati primerne skupinske vadbe
- pojasni, katere vadbe so primerne za njegov cilj
- po potrebi predlagaj izdelavo TEDENSKEGA razporeda SKUPINSKIH VADB
- postavljaj dodatna vprašanja, če podatki manjkajo
"""

# -------------------------------------------------
# Chat function
# -------------------------------------------------
def chat_with_ai(messages: List[Dict[str, str]]) -> str:
    """
    Stateless AI chat.
    Frontend sends full conversation context each time.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content

    except Exception:
        # 🔒 production-safe fallback
        return (
            "Oprosti, trenutno imam težave pri odgovarjanju. "
            "Poskusi znova čez trenutek."
        )