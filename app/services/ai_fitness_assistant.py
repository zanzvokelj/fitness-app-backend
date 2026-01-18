from openai import OpenAI
from app.core.config import settings

# OpenAI client (lazy usage, safe for prod)
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


def explain_recommendation_test() -> str:
    """
    Simple test call to verify OpenAI connectivity.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in Slovenian."},
        ],
        max_tokens=20,
    )

    return response.choices[0].message.content