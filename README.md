# 🦫 BEAVER — Local Voice Assistant

A fully offline, voice-controlled assistant for Windows with an over-the-top dark
HUD. Say a wake word + command and it shows maps, videos, weather, and search
right inside the app. Speech recognition and text-to-speech run entirely on your
machine — no accounts, no API keys, completely free.

## Setup (Windows)

You need **Python 3.9+** ([python.org](https://www.python.org/downloads/) — tick
*Add Python to PATH* during install).

1. Unzip this folder anywhere.
2. Double-click **`setup.bat`** (creates a virtual environment and installs
   dependencies). Run once.
3. Double-click **`start_beaver.bat`**.
4. On first launch, click **INSTALL VOICE MODEL** — it downloads and installs the
   offline model inside the app, with a progress bar. Then click **ENTER BEAVER**.
5. Click **WAKE BEAVER**, allow microphone access, and start talking.

## Say "beaver" + a command

| Say | Result |
|-----|--------|
| `beaver open maps of Vancouver` | Map in the viewport |
| `beaver play lofi beats` | YouTube results |
| `beaver weather in London` | Live weather panel |
| `beaver search for SpaceX` | Search results |
| `beaver tell me about beavers` | Wikipedia |
| `beaver what time is it` | Time card |
| `beaver open calculator` | Launches calculator |
| `beaver news` | Headlines |
| `beaver clear` | Clears the viewport |

There's also a text box if you'd rather type.

## Stack (all free / open source)

Python · Vosk (offline speech-to-text) · pyttsx3 (offline TTS) · Eel · sounddevice

## Troubleshooting

- **requirements.txt not found** — `setup.bat` now runs from its own folder
  automatically; just keep all the files together.
- **Model install fails** — check your internet connection and click retry. The
  app installs the model on first run; you don't need to download anything by hand.
- **No mic input** — Settings → Privacy → Microphone, and confirm your input
  device is the default.
- **Embedded video/maps blank** — some sites block iframes; the command still
  opens them in your real browser as a fallback.
