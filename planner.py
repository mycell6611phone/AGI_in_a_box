"""
planner.py
~~~~~~~~~~

Purpose:
Generates, organizes, and manages multi-step plans or action sequences for the AGI agent.
Each plan can be created, listed, completed, or removed. In future, plans may be scored by risk/reward or resource cost.
"""

import uuid
from datetime import datetime

class Planner:
    """Responsible for orchestrating candidate actions and multi-step plans."""

    def __init__(self) -> None:
        """
        Initialize plan storage.
        - `self._plans` holds plan_id → plan structure mappings.
        """
        self._plans: dict[str, dict] = {}
        print("[Planner] Initialized plan registry")

    def create_plan(self, goal: str, steps: list[str]) -> str:
        """
        Create a new plan based on a provided goal and steps.

        Args:
            goal: Natural language description of the intended outcome.
            steps: List of steps (str) to execute toward the goal.

        Returns:
            A unique plan ID for reference.
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        self._plans[plan_id] = {
            "goal": goal,
            "steps": steps,
            "created": datetime.utcnow().isoformat(),
            "completed": False,
            "results": []
        }
        print(f"[Planner] Created plan: {plan_id}")
        return plan_id

    def list_plans(self) -> dict:
        """Return all current plans."""
        return self._plans

    def complete_step(self, plan_id: str, result: str) -> bool:
        """
        Mark the next step as completed and store its result.
        If all steps are done, marks the plan complete.

        Returns:
            True if successful, False otherwise.
        """
        if plan_id not in self._plans:
            return False

        plan = self._plans[plan_id]
        if not plan["steps"]:
            return False

        plan["results"].append(result)
        plan["steps"].pop(0)

        if not plan["steps"]:
            plan["completed"] = True
            print(f"[Planner] Plan {plan_id} completed.")

        return True

    def delete_plan(self, plan_id: str) -> bool:
        """
        Remove a plan from memory.
        """
        if plan_id in self._plans:
            del self._plans[plan_id]
            print(f"[Planner] Deleted plan: {plan_id}")
            return True
        return False
