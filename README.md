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
| `beaver what apps are open` | Lists running applications |
| `beaver open windows` | Lists open window titles |
| `beaver current tab` | Names your active browser tab |
| `beaver recent files` | Recent files from Downloads/Documents/Desktop |
| `beaver research electric cars` | Searches, compares sources, writes a report (saved + shown) |
| `beaver go to github` | Navigates to a site in-app |
| `beaver open maps of Vancouver` | Map in the viewport |
| `beaver play lofi beats` | Plays a YouTube video in-app |
| `beaver weather in London` | Live weather panel |
| `beaver search for SpaceX` | Search results |
| `beaver tell me about beavers` | Wikipedia |
| `beaver what time is it` | Time card |
| `beaver open calculator` | Launches calculator |
| `beaver how do you feel` | Reports your detected mood |
| `beaver clear` | Clears the viewport |

Beaver also detects your **emotional tone** from what you say (shown as a chip in
the top bar) and adapts its replies — e.g. if you sound frustrated, it keeps
things brief and reassuring. Reports are saved as Markdown in the `reports/`
folder and displayed in-app.

### Build websites & apps by voice
Say things like **"make me a simple website for a bakery"**, "build a calculator
app", or "create a portfolio page". Beaver generates a complete, working site and
shows it live in the viewport. Test it right there, then just say what to change
("make the background green", "add a contact form") and it updates the same site,
remembering context. Finished sites are saved in the `generated_sites/` folder.
This uses the Anthropic API — create a file named **`api_key.txt`** in the Beaver
folder with your key inside (from console.anthropic.com). Everything else works
without it.

### Interrupt
While Beaver is speaking, just start talking — it stops and listens. There's also
a 🔇 button to silence it instantly.

### Mini mode (always-on-top)
Click 📌 to shrink Beaver into a compact panel pinned to the bottom-right corner,
always on top. Click again to restore.

There's also a text box if you'd rather type.

### Notes on a couple of features
- **Browser tabs:** Windows only exposes the *active* tab's title to other apps,
  so Beaver reports the focused tab — not a full list of every open tab.
- **Files:** Beaver scans Downloads, Documents, and Desktop by default. Change
  `SCAN_FOLDERS` in `core/config.py` to adjust.
- **Research/reports & site building** need internet at runtime; everything else
  works offline.

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
