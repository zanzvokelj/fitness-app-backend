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
Si profesionalni fitnes trener in svetovalec.

Tvoja naloga:
- odgovarjaj kratko, jasno in prijazno
- postavljaj vprašanja, kadar podatki manjkajo
- NE izmišljaj si terminov ali cen
- kadar je primerno, predlagaj izdelavo vadbenega plana
- uporabljaj slovenščino
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