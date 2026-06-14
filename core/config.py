import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model")

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_FOLDER_NAME = "vosk-model-small-en-us-0.15"

WAKE_WORD = "beaver"
REQUIRE_WAKE_WORD = False
FOLLOWUP_WINDOW = 6.0

TTS_RATE = 175
TTS_VOICE_INDEX = None

GREETING = "Beaver online. Ready when you are."

BROWSER_MODE = "chrome"

DEFAULT_CITY = ""
