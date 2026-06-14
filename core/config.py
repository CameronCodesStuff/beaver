import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model")

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_FOLDER_NAME = "vosk-model-small-en-us-0.15"

MODEL_URL_LARGE = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
MODEL_FOLDER_NAME_LARGE = "vosk-model-en-us-0.22"

WAKE_WORD = "beaver"
REQUIRE_WAKE_WORD = False
INTERRUPTIBLE = True
FOLLOWUP_WINDOW = 6.0

TTS_RATE = 175
TTS_VOICE_INDEX = None

GREETING = "Beaver online. Ready when you are."

BROWSER_MODE = "chrome"

DEFAULT_CITY = ""

SCAN_FOLDERS = ["Downloads", "Documents", "Desktop"]
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SITES_DIR = os.path.join(BASE_DIR, "generated_sites")
