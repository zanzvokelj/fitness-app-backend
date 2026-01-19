# app/ai/logic.py
from datetime import date
from collections import defaultdict

from app.models.session import Session
from app.ai.rules import GOAL_CLASS_PRIORITY, SUPPORT_CLASSES


def recommend_sessions(
    *,
    goal: str,
    days_per_week: int,
    sessions: list[Session],
) -> list[Session]:
    """
    Returns a list of concrete Session objects
    """

    priority = GOAL_CLASS_PRIORITY.get(goal, [])

    # filter only future sessions with free spots
    available = [
        s for s in sessions
        if s.start_time.date() >= date.today()
        and s.booked_count < s.capacity
    ]

    # group sessions by class name
    sessions_by_class = defaultdict(list)
    for s in available:
        sessions_by_class[s.class_type.name].append(s)

    selected = []
    used_classes = set()

    for class_name in priority:
        if class_name not in sessions_by_class:
            continue

        for session in sessions_by_class[class_name]:
            if len(selected) >= days_per_week:
                break

            # avoid same class twice if possible
            if class_name in used_classes:
                continue

            selected.append(session)
            used_classes.add(class_name)

        if len(selected) >= days_per_week:
            break

    return selected

