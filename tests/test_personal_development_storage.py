import unittest
from unittest.mock import patch

from brain.personal_development import PersonalDevelopment


class PersonalDevelopmentStorageTests(unittest.TestCase):
    def test_goal_done_skips_malformed_records(self):
        goals = [
            None,
            {"id": "not-a-number", "title": "Broken goal", "status": "active"},
            {"id": 7, "title": "Valid goal", "status": "active"},
        ]

        with patch("brain.personal_development.memory.get", return_value=goals), \
             patch("brain.personal_development.memory.set") as save:
            changed = PersonalDevelopment().goal_done(7)

        self.assertTrue(changed)
        self.assertEqual(goals[2]["status"], "completed")
        save.assert_called_once()

    def test_habit_log_skips_malformed_records(self):
        habits = [
            None,
            {"id": "not-a-number", "name": "Broken habit", "logs": []},
            {"id": 8, "name": "Valid habit", "logs": []},
        ]

        with patch("brain.personal_development.memory.get", return_value=habits), \
             patch("brain.personal_development.memory.set") as save:
            changed = PersonalDevelopment().habit_log(8, "2026-01-01")

        self.assertTrue(changed)
        self.assertEqual(habits[2]["logs"], ["2026-01-01"])
        save.assert_called_once()

    def test_habit_log_does_not_duplicate_date(self):
        habits = [
            {"id": 8, "name": "Reading", "logs": ["2026-01-01"]},
        ]

        with patch("brain.personal_development.memory.get", return_value=habits), \
             patch("brain.personal_development.memory.set") as save:
            changed = PersonalDevelopment().habit_log(8, "2026-01-01")

        self.assertTrue(changed)
        self.assertEqual(habits[0]["logs"], ["2026-01-01"])
        save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
