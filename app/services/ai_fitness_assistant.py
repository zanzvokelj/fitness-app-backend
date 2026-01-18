from openai import OpenAI
from app.core.config import settings

# OpenAI client (safe for prod – AI is non-critical layer)
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
    Uses OpenAI to generate a human-friendly explanation
    for the rule-based fitness recommendation.

    IMPORTANT:
    - AI is a non-critical layer
    - Failure must NEVER break the API
    """

    session_list = "\n".join(
        f"- {s['class']} on {s['date']} at {s['time']}"
        for s in sessions
    )

    ticket_text = (
        f"Recommended ticket: {ticket['name']} ({ticket['price']} €)"
        if ticket
        else "No ticket recommendation available."
    )

    prompt = f"""
You are a professional fitness coach.

User goal: {goal}
Experience level: {experience_level}
Trainings per week: {days_per_week}

Recommended sessions:
{session_list}

{ticket_text}

Explain briefly:
- why these sessions fit the goal
- why this ticket makes sense
- add one short motivational sentence
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful fitness assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.6,
            max_tokens=200,
        )

        return response.choices[0].message.content

    except Exception:
        # 🔐 Fallback – NEVER break core functionality
        return (
            "These sessions are well balanced for your goal and weekly "
            "schedule. Stay consistent, focus on proper recovery, "
            "and remember that progress comes from regular effort."
        )


def explain_recommendation_test() -> str:
    """
    Simple test call to verify OpenAI connectivity.
    This endpoint is safe and isolated from core logic.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in Slovenian."},
            ],
            max_tokens=20,
        )

        return response.choices[0].message.content

    except Exception:
        return "Pozdravljen! (AI trenutno ni na voljo)"