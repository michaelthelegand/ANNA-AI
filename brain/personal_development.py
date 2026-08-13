from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from brain.memory import memory


@dataclass
class PersonalDevelopment:
    goals_key: str = "pd_goals"
    goal_next_id_key: str = "pd_goal_next_id"
    habits_key: str = "pd_habits"
    habit_next_id_key: str = "pd_habit_next_id"

    def _now_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _today(self) -> str:
        return date.today().isoformat()

    def _load_list(self, key: str) -> list[dict[str, Any]]:
        data = memory.get(key, [])
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict)]

    def _save_list(self, key: str, items: list[dict[str, Any]]) -> None:
        memory.set(key, items)

    def _next_id(self, key: str) -> int:
        current = memory.get(key, 1)
        try:
            next_id = int(current)
        except (TypeError, ValueError, OverflowError):
            next_id = 1

        memory.set(key, next_id + 1)
        return next_id

    # -------------------------
    # Goals
    # -------------------------
    def goal_add(
        self,
        title: str,
        why: str = "",
        target_date: str | None = None,
    ) -> dict[str, Any]:
        clean_title = (title or "").strip()
        if not clean_title:
            raise ValueError("Goal title is empty.")

        goals = self._load_list(self.goals_key)
        goal = {
            "id": self._next_id(self.goal_next_id_key),
            "title": clean_title,
            "why": (why or "").strip(),
            "target_date": (target_date or "").strip() or None,
            "status": "active",
            "created_utc": self._now_utc(),
            "completed_utc": None,
        }
        goals.append(goal)
        self._save_list(self.goals_key, goals)
        return goal

    def goal_list(self, include_completed: bool = False) -> list[dict[str, Any]]:
        goals = self._load_list(self.goals_key)
        if include_completed:
            return goals
        return [goal for goal in goals if goal.get("status") != "completed"]

    def goal_done(self, goal_id: int) -> bool:
        try:
            target_id = int(goal_id)
        except (TypeError, ValueError, OverflowError):
            return False

        goals = self._load_list(self.goals_key)
        for goal in goals:
            try:
                current_id = int(goal.get("id", -1))
            except (TypeError, ValueError, OverflowError):
                continue

            if current_id == target_id and goal.get("status") != "completed":
                goal["status"] = "completed"
                goal["completed_utc"] = self._now_utc()
                self._save_list(self.goals_key, goals)
                return True

        return False

    def goal_clear_completed(self) -> int:
        goals = self._load_list(self.goals_key)
        remaining = [
            goal for goal in goals if goal.get("status") != "completed"
        ]
        removed = len(goals) - len(remaining)
        self._save_list(self.goals_key, remaining)
        return removed

    # -------------------------
    # Habits
    # -------------------------
    def habit_add(
        self,
        name: str,
        frequency: str = "daily",
    ) -> dict[str, Any]:
        clean_name = (name or "").strip()
        if not clean_name:
            raise ValueError("Habit name is empty.")

        clean_frequency = (frequency or "daily").strip().lower()
        habits = self._load_list(self.habits_key)

        for habit in habits:
            if str(habit.get("name", "")).lower() == clean_name.lower():
                raise ValueError("Habit already exists.")

        habit = {
            "id": self._next_id(self.habit_next_id_key),
            "name": clean_name,
            "frequency": clean_frequency or "daily",
            "created_utc": self._now_utc(),
            "logs": [],
        }
        habits.append(habit)
        self._save_list(self.habits_key, habits)
        return habit

    def habit_list(self) -> list[dict[str, Any]]:
        return self._load_list(self.habits_key)

    def habit_log(
        self,
        habit_id: int,
        logged_date: str | None = None,
    ) -> bool:
        try:
            target_id = int(habit_id)
        except (TypeError, ValueError, OverflowError):
            return False

        day = (logged_date or self._today()).strip()
        habits = self._load_list(self.habits_key)

        for habit in habits:
            try:
                current_id = int(habit.get("id", -1))
            except (TypeError, ValueError, OverflowError):
                continue

            if current_id != target_id:
                continue

            logs = habit.get("logs", [])
            if not isinstance(logs, list):
                logs = []

            if day not in logs:
                logs.append(day)
                habit["logs"] = sorted(set(str(item) for item in logs))
                self._save_list(self.habits_key, habits)

            return True

        return False

    # -------------------------
    # Progress
    # -------------------------
    def progress(self) -> dict[str, Any]:
        goals = self._load_list(self.goals_key)
        habits = self._load_list(self.habits_key)

        completed_goals = sum(
            1 for goal in goals if goal.get("status") == "completed"
        )
        today = self._today()
        habits_done_today = sum(
            1 for habit in habits
            if today in habit.get("logs", [])
        )

        return {
            "goals_total": len(goals),
            "goals_completed": completed_goals,
            "goals_active": len(goals) - completed_goals,
            "habits_total": len(habits),
            "habits_done_today": habits_done_today,
            "today": today,
        }


personal_development = PersonalDevelopment()
