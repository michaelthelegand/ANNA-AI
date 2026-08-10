import unittest
from unittest.mock import Mock, patch

from voice.text_to_speech import TextToSpeech


class TextToSpeechTests(unittest.TestCase):
    @patch("voice.text_to_speech.pyttsx3.init")
    def test_engine_initializes_lazily(self, init_mock):
        engine = Mock()
        engine.getProperty.return_value = []
        init_mock.return_value = engine

        speech = TextToSpeech()

        init_mock.assert_not_called()

        speech.speak("  Hello ANNA  ", wait=False)

        init_mock.assert_called_once_with()
        engine.say.assert_called_once_with("Hello ANNA")
        engine.runAndWait.assert_called_once_with()

    @patch("voice.text_to_speech.pyttsx3.init")
    def test_empty_text_is_ignored(self, init_mock):
        speech = TextToSpeech()

        speech.speak("   ")

        init_mock.assert_not_called()

    @patch("voice.text_to_speech.pyttsx3.init")
    def test_stop_before_initialization_is_safe(self, init_mock):
        speech = TextToSpeech()

        speech.stop()

        init_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
