# goal_manager.py

import os, json
from datetime import datetime

# adjust this path if your code lives elsewhere
GOALS_FILE = os.path.expanduser(
    "~/Desktop/AGI_in_A_box_v2/legacy_modules/goals.json"
)

def log_goals(goals: str) -> str:
    """
    Append a new goal (any granularity) to goals.json and return a confirmation.
    """
    os.makedirs(os.path.dirname(GOALS_FILE), exist_ok=True)
    try:
        goals = json.load(open(GOALS_FILE))
    except Exception:
        goals = []
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "goals": goal
    }
    goals.append(entry)
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)
    return f"[GoalManager] Logged: {goals!r}"

def get_goals() -> str:
    """
    Return all persisted goals as a JSON-encoded list of {timestamp,goals}.
    """
    try:
        return json.dumps(json.load(open(GOALS_FILE)), indent=2)
    except Exception:
        return "[]"

