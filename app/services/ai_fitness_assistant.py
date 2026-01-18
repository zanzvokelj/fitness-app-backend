# app/services/ai_fitness_assistant.py

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
    Generates a human-friendly explanation for the fitness recommendation.
    This is a PURE AI layer – no business logic here.
    """

    if not sessions:
        return "No suitable training sessions were found for your preferences."

    session_list = "\n".join(
        f"- {s['class']} on {s['date']} at {s['time']}"
        for s in sessions
    )

    ticket_text = (
        f"Recommended ticket: {ticket['name']} ({ticket['price']} €)"
        if ticket
        else "No ticket recommendation available"
    )

    prompt = f"""
You are a professional fitness coach and personal trainer.

User goal: {goal}
Experience level: {experience_level}
Trainings per week: {days_per_week}

Recommended training sessions:
{session_list}

{ticket_text}

Explain in a friendly and motivating tone:
- why these sessions match the user's goal and experience level
- how often the user should train weekly
- why this ticket is a good financial choice
- give ONE short motivational tip at the end

Keep the response concise and practical.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful and motivating fitness assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()