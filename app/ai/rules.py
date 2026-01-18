# app/ai/rules.py

GOAL_CLASS_PRIORITY = {
    "fat_loss": ["Kickbox", "BodyPump", "Core", "BodyBalance"],
    "strength": ["BodyPump", "Core", "Kickbox", "BodyBalance"],
    "mobility": ["BodyBalance", "Core"]
}

SUPPORT_CLASSES = ["Core", "BodyBalance"]
HIIT_CLASSES = ["Kickbox"]