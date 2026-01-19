from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def explain_recommendation(
    *,
    goal: str,
    days_per_week: int,
    experience_level: str,
    sessions: list[dict],
    ticket: dict | None,
) -> str:
    """
    Generates a human-friendly explanation for a WEEKLY training plan.
    """

    # ✅ FIX: use day instead of date
    session_list = "\n".join(
        f"- {s['day']}: {s['class']} ob {s['time']}"
        for s in sessions
    )

    ticket_text = (
        f"{ticket['name']} ({ticket['price']} €) – {ticket.get('reason', '')}"
        if ticket
        else "Trenutno ni primerne karte."
    )

    prompt = f"""
Si profesionalni fitnes trener.

Cilj uporabnika: {goal}
Stopnja izkušenosti: {experience_level}
Vadbe na teden: {days_per_week}

Tedenski plan vadb:
{session_list}

Priporočena karta:
{ticket_text}

Na kratko pojasni:
- zakaj je ta razpored primeren
- zakaj je karta smiselna
- dodaj eno motivacijsko misel
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful fitness assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=200,
        )
        return response.choices[0].message.content

    except Exception:
        # 🔒 graceful fallback (VERY IMPORTANT for prod)
        return (
            "Izbran program ponuja dobro ravnovesje med intenzivnimi "
            "in podporno-regeneracijskimi vadbami. "
            "Doslednost je ključ do dolgoročnih rezultatov 💪"
        )


def explain_recommendation_test() -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Pozdravi v slovenščini."},
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content