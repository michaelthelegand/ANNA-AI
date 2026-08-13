import unittest
from unittest.mock import patch

from brain.reasoning import Reasoner


class PersonalDevelopmentCommandTests(unittest.TestCase):
    def setUp(self):
        self.reasoner = Reasoner(name="Test")

    def run_command_without_saving(self, command):
        with patch.object(self.reasoner, "_load_history", return_value=[]), \
             patch.object(self.reasoner, "_append_history"), \
             patch.object(self.reasoner, "_save_history"):
            return self.reasoner.respond(command)

    def test_goal_add_command_creates_goal(self):
        goal = {"id": 1, "title": "Learn Python"}

        with patch(
            "brain.reasoning.personal_development.goal_add",
            return_value=goal,
        ) as goal_add:
            response = self.run_command_without_saving("goal add Learn Python")

        goal_add.assert_called_once_with("Learn Python")
        self.assertIn("Added goal #1", response)
        self.assertIn("Learn Python", response)

    def test_goal_done_command_completes_goal(self):
        with patch(
            "brain.reasoning.personal_development.goal_done",
            return_value=True,
        ) as goal_done:
            response = self.run_command_without_saving("goal done 1")

        goal_done.assert_called_once_with(1)
        self.assertIn("Marked goal #1 completed", response)

    def test_habit_add_command_accepts_frequency(self):
        habit = {
            "id": 1,
            "name": "Read 10 pages",
            "frequency": "weekly",
        }

        with patch(
            "brain.reasoning.personal_development.habit_add",
            return_value=habit,
        ) as habit_add:
            response = self.run_command_without_saving(
                "habit add Read 10 pages weekly"
            )

        habit_add.assert_called_once_with("Read 10 pages", "weekly")
        self.assertIn("Added habit #1", response)
        self.assertIn("Read 10 pages", response)

    def test_habit_log_command_logs_date(self):
        with patch(
            "brain.reasoning.personal_development.habit_log",
            return_value=True,
        ) as habit_log:
            response = self.run_command_without_saving(
                "habit log 2 2026-01-15"
            )

        habit_log.assert_called_once_with(2, "2026-01-15")
        self.assertIn("Logged habit #2", response)

    def test_progress_command_returns_summary(self):
        summary = {
            "today": "2026-01-15",
            "goals_completed": 2,
            "goals_total": 5,
            "goals_active": 3,
            "habits_done_today": 4,
            "habits_total": 6,
        }

        with patch(
            "brain.reasoning.personal_development.progress",
            return_value=summary,
        ) as progress:
            response = self.run_command_without_saving("progress")

        progress.assert_called_once_with()
        self.assertIn("2/5 completed", response)
        self.assertIn("Habits done today: 4/6", response)


if __name__ == "__main__":
    unittest.main()
