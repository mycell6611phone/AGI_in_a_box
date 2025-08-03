"""
goal_manager.py
~~~~~~~~~~~~~~~

Purpose:
Tracks goals submitted to the AGI system. Goals can be added, retrieved, updated, and marked complete.
Includes metadata such as creation date, status, and number of attempts.
"""

import uuid
from datetime import datetime

class GoalManager:
    def __init__(self):
        self._goals: dict[str, dict] = {}
        print("[GoalManager] Initialized goal tracker")

    def add_goal(self, description: str) -> str:
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        self._goals[goal_id] = {
            "description": description,
            "created": datetime.utcnow().isoformat(),
            "status": "pending",
            "attempts": 0,
            "completed": False
        }
        print(f"[GoalManager] Added goal: {goal_id}")
        return goal_id

    def get_goal(self, goal_id: str) -> dict:
        return self._goals.get(goal_id, {})

    def list_goals(self, include_completed: bool = False) -> dict:
        if include_completed:
            return self._goals
        return {k: v for k, v in self._goals.items() if not v["completed"]}

    def mark_completed(self, goal_id: str) -> bool:
        if goal_id in self._goals:
            self._goals[goal_id]["completed"] = True
            self._goals[goal_id]["status"] = "done"
            print(f"[GoalManager] Goal completed: {goal_id}")
            return True
        return False

    def increment_attempt(self, goal_id: str) -> None:
        if goal_id in self._goals:
            self._goals[goal_id]["attempts"] += 1
