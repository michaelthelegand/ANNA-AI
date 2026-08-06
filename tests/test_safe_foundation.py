from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from brain.memory import MemoryStore
from control.automation import Automation
from tools.terminal import TerminalTool, TerminalToolError


class SafeFoundationTests(unittest.TestCase):
    def test_memory_store_creates_and_reads_values(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            store = MemoryStore(path=path)

            self.assertTrue(path.exists())
            self.assertIsNone(store.get("missing"))
            store.set("favorite_color", "blue")
            self.assertEqual(store.get("favorite_color"), "blue")

    def test_automation_status_is_read_only(self):
        status = Automation().status()

        self.assertIn("automation_enabled", status)
        self.assertIn("keyboard_enabled", status)
        self.assertIn("mouse_enabled", status)
        self.assertIn("windows_enabled", status)
        self.assertEqual(status["supported_actions"], [])

    def test_terminal_is_disabled_by_default_instance(self):
        terminal = TerminalTool(enabled=False)

        with self.assertRaises(TerminalToolError):
            terminal.run("where python")


if __name__ == "__main__":
    unittest.main()
