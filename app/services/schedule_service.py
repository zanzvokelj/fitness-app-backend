from sqlalchemy import text

from sqlalchemy.orm import Session

WEEKDAYS_SI = {
    1: "Ponedeljek",
    2: "Torek",
    3: "Sreda",
    4: "Četrtek",
    5: "Petek",
    6: "Sobota",
    0: "Nedelja",
}

def get_weekly_schedule_text(db: Session) -> str:
    rows = db.execute(text("""
        SELECT weekday, class_name, start_time, end_time
        FROM weekly_schedule
        ORDER BY weekday, start_time
    """)).fetchall()

    schedule = {}
    for r in rows:
        day = WEEKDAYS_SI[r.weekday]
        schedule.setdefault(day, []).append(
            f"- {r.start_time.strftime('%H:%M')}–{r.end_time.strftime('%H:%M')} {r.class_name}"
        )

    return "\n".join(
        f"{day}:\n" + "\n".join(items)
        for day, items in schedule.items()
    )