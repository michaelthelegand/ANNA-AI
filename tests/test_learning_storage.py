import unittest
from unittest.mock import patch

from brain.learning import Learner


class LearnerTodoStorageTests(unittest.TestCase):
    def test_todo_done_skips_malformed_records(self):
        todos = [
            None,
            {"id": "not-a-number", "text": "Broken item", "done": False},
            {"id": 7, "text": "Valid item", "done": False},
        ]

        with patch("brain.learning.memory.get", return_value=todos), \
             patch("brain.learning.memory.set") as save:
            changed = Learner().todo_done(7)

        self.assertTrue(changed)
        self.assertTrue(todos[2]["done"])
        save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
