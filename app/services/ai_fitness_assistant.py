# app/services/ai_fitness_assistant.py

from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def explain_recommendation(
    *,
    goal: str,
    days_per_week: int,
    sessions: list[dict],
    ticket: dict | None,
) -> str:
    session_list = "\n".join(
        f"- {s['class']} on {s['date']} at {s['time']}"
        for s in sessions
    )

    ticket_text = (
        f"Recommended ticket: {ticket['name']} ({ticket['price']}€)"
        if ticket
        else "No ticket recommendation available"
    )

    prompt = f"""
You are a professional fitness coach.

User goal: {goal}
Trainings per week: {days_per_week}

Recommended sessions:
{session_list}

{ticket_text}

Explain shortly:
- why these sessions fit the goal
- why this ticket makes sense
- one motivational sentence
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