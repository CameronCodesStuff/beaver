import os
import json
import threading
import time

import eel

from core.speech import SpeechEngine
from core.tts import Speaker
from core.commands import CommandRouter
from core import config, installer

speaker = Speaker()
router = CommandRouter(speaker)
speech = None
listening = False
_listen_thread = None


def ui_status(text):
    try:
        eel.setStatus(text)
    except Exception:
        pass


def ui_log(role, text):
    try:
        eel.addLog(role, text)
    except Exception:
        pass


def ui_action(action):
    try:
        eel.fireAction(json.dumps(action))
    except Exception:
        pass


router.bind_ui(ui_log, ui_action, ui_status)


@eel.expose
def model_status():
    return {"ready": installer.model_ready()}


@eel.expose
def install_model():
    def progress(pct, msg):
        try:
            eel.installProgress(pct, msg)
        except Exception:
            pass

    def worker():
        ok = installer.install_model(progress)
        try:
            eel.installDone(ok)
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()
    return {"started": True}


@eel.expose
def start_listening():
    global listening, _listen_thread, speech
    if listening:
        return {"ok": True, "already": True}

    if not installer.model_ready():
        return {"ok": False, "error": "model_missing"}

    if speech is None:
        try:
            speech = SpeechEngine(config.MODEL_PATH, on_partial=_on_partial)
        except Exception as e:
            ui_log("system", f"Speech engine failed: {e}")
            return {"ok": False, "error": "engine_failed", "message": str(e)}

    listening = True
    _listen_thread = threading.Thread(target=_listen_loop, daemon=True)
    _listen_thread.start()
    ui_status("LISTENING")
    speaker.say(config.GREETING)
    ui_log("beaver", config.GREETING)
    return {"ok": True}


@eel.expose
def stop_listening():
    global listening
    listening = False
    ui_status("STANDBY")
    return {"ok": True}


@eel.expose
def send_text_command(text):
    if not text:
        return
    ui_log("user", text)
    router.handle(text.lower().strip())


@eel.expose
def get_wake_word():
    return config.WAKE_WORD


def _on_partial(text):
    try:
        eel.setPartial(text)
    except Exception:
        pass


def _listen_loop():
    global listening
    wake = config.WAKE_WORD.lower()
    awake_until = 0

    for text in speech.results():
        if not listening:
            break
        text = text.lower().strip()
        if not text:
            continue

        if config.REQUIRE_WAKE_WORD:
            now = time.time()
            if wake not in text and now >= awake_until:
                _on_partial(text)
                continue
            awake_until = time.time() + config.FOLLOWUP_WINDOW

        cmd = text.replace(wake, "").strip()
        ui_log("user", text)
        if cmd:
            router.handle(cmd)
        else:
            speaker.say("Yes?")
            ui_log("beaver", "Yes?")

    listening = False
    ui_status("STANDBY")


def main():
    eel.init("web")
    print("Beaver starting…  UI at http://localhost:8000")
    try:
        eel.start(
            "index.html",
            size=(1240, 800),
            position=(70, 50),
            mode=config.BROWSER_MODE,
            block=True,
        )
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as e:
        print(f"App-mode launch failed ({e}); opening default browser.")
        eel.start("index.html", size=(1240, 800), mode="default", block=True)


if __name__ == "__main__":
    main()
