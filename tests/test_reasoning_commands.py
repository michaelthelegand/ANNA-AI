import unittest
from unittest.mock import patch

from brain.reasoning import Reasoner


class ReasoningCommandTests(unittest.TestCase):
    def setUp(self):
        self.reasoner = Reasoner(name="Test")

    def run_command_without_saving(self, command):
        with patch.object(self.reasoner, "_load_history", return_value=[]), \
             patch.object(self.reasoner, "_append_history"), \
             patch.object(self.reasoner, "_save_history"):
            return self.reasoner.respond(command)

    def test_help_command_returns_help_text(self):
        response = self.run_command_without_saving("help")
        self.assertIsInstance(response, str)
        self.assertIn("help", response.lower())

    def test_automation_command_reports_disabled_status(self):
        response = self.run_command_without_saving("automation")
        lowered = response.lower()
        self.assertIn("automation", lowered)
        self.assertIn("false", lowered)

    def test_status_command_returns_status_text(self):
        response = self.run_command_without_saving("status")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response.strip()) > 0)


if __name__ == "__main__":
    unittest.main()
