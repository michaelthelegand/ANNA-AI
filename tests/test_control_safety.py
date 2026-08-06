import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from control.keyboard import KeyboardControl, KeyboardControlError
from control.mouse import MouseControl, MouseControlError
from control.windows import WindowsControl, WindowsControlError


class ControlSafetyTests(unittest.TestCase):
    def test_keyboard_actions_are_disabled(self):
        keyboard = KeyboardControl(enabled=False)

        with self.assertRaises(KeyboardControlError):
            keyboard.type_text("test")

        with self.assertRaises(KeyboardControlError):
            keyboard.press("enter")

        with self.assertRaises(KeyboardControlError):
            keyboard.hotkey("ctrl", "c")

    def test_mouse_is_disabled(self):
        mouse = MouseControl(enabled=False)

        with self.assertRaises(MouseControlError):
            mouse.position()

    def test_windows_actions_are_disabled(self):
        windows = WindowsControl(enabled=False)

        with self.assertRaises(WindowsControlError):
            windows.open_path(".")

        with self.assertRaises(WindowsControlError):
            windows.reveal_in_explorer(".")

    def test_windows_rejects_paths_outside_project(self):
        with TemporaryDirectory() as folder:
            base_dir = Path(folder) / "project"
            base_dir.mkdir()
            outside_file = Path(folder) / "outside.txt"
            outside_file.write_text("blocked", encoding="utf-8")

            windows = WindowsControl(base_dir=base_dir, enabled=True)

            with self.assertRaises(WindowsControlError):
                windows.open_path(outside_file)


if __name__ == "__main__":
    unittest.main()
