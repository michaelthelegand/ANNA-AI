import unittest
from unittest.mock import patch

from brain.reasoning import Reasoner


class CommandSafetyTests(unittest.TestCase):
    def setUp(self):
        self.reasoner = Reasoner(name="Test")

    def run_command_without_saving(self, command):
        with patch.object(self.reasoner, "_load_history", return_value=[]), \
             patch.object(self.reasoner, "_append_history"), \
             patch.object(self.reasoner, "_save_history"):
            return self.reasoner.respond(command)

    def test_unknown_command_returns_text(self):
        response = self.run_command_without_saving("this_command_does_not_exist")
        self.assertIsInstance(response, str)
        self.assertTrue(response.strip())

    def test_incomplete_commands_do_not_crash(self):
        commands = [
            "read",
            "write",
            "run",
            "search",
            "openurl",
            "remember",
            "recall",
            "todo",
            "press",
            "hotkey",
            "type",
        ]

        for command in commands:
            with self.subTest(command=command):
                response = self.run_command_without_saving(command)
                self.assertIsInstance(response, str)
                self.assertTrue(response.strip())


if __name__ == "__main__":
    unittest.main()
