# app/ai/logic.py
from collections import defaultdict
from app.models.session import Session
from app.ai.rules import GOAL_CLASS_PRIORITY


def recommend_sessions(
    *,
    goal: str,
    days_per_week: int,
    sessions: list[Session],
) -> list[Session]:
    """
    Weekly recommendation:
    - max 1 session per weekday
    - ignore capacity & dates
    - follow goal priority
    """

    priority = GOAL_CLASS_PRIORITY.get(goal, [])

    sessions_by_weekday: dict[int, list[Session]] = defaultdict(list)
    for s in sessions:
        sessions_by_weekday[s.start_time.weekday()].append(s)

    selected: list[Session] = []
    used_weekdays = set()

    for class_name in priority:
        for weekday in sorted(sessions_by_weekday.keys()):
            if len(selected) >= days_per_week:
                return selected

            if weekday in used_weekdays:
                continue

            for session in sessions_by_weekday[weekday]:
                if session.class_type.name == class_name:
                    selected.append(session)
                    used_weekdays.add(weekday)
                    break

    return selected