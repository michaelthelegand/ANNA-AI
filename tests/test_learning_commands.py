import unittest
from unittest.mock import patch

from brain.reasoning import Reasoner


class LearningCommandTests(unittest.TestCase):
    def setUp(self):
        self.reasoner = Reasoner(name="Test")

    def run_command_without_saving(self, command):
        with patch.object(self.reasoner, "_load_history", return_value=[]), \
             patch.object(self.reasoner, "_append_history"), \
             patch.object(self.reasoner, "_save_history"):
            return self.reasoner.respond(command)

    def test_remember_command_saves_fact(self):
        with patch("brain.reasoning.learner.remember") as remember:
            response = self.run_command_without_saving("remember favorite color = blue")

        remember.assert_called_once_with("favorite color", "blue")
        self.assertIn("Remembered favorite color", response)

    def test_recall_command_returns_saved_fact(self):
        with patch("brain.reasoning.learner.recall", return_value="blue") as recall:
            response = self.run_command_without_saving("recall favorite color")

        recall.assert_called_once_with("favorite color", default=None)
        self.assertIn("favorite color = blue", response)

    def test_todo_add_command_creates_todo(self):
        todo = {"id": 1, "text": "Test ANNA", "done": False}

        with patch("brain.reasoning.learner.todo_add", return_value=todo) as todo_add:
            response = self.run_command_without_saving("todo add Test ANNA")

        todo_add.assert_called_once_with("Test ANNA")
        self.assertIn("Added TODO #1", response)
        self.assertIn("Test ANNA", response)

    def test_todo_done_command_marks_todo_done(self):
        with patch("brain.reasoning.learner.todo_done", return_value=True) as todo_done:
            response = self.run_command_without_saving("todo done 1")

        todo_done.assert_called_once_with(1)
        self.assertIn("Marked TODO #1 done", response)


if __name__ == "__main__":
    unittest.main()
