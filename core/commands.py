import re
import datetime
import urllib.parse
import subprocess
import platform


class CommandRouter:
    def __init__(self, speaker):
        self.speaker = speaker
        self._log = lambda role, text: None
        self._action = lambda action: None
        self._status = lambda text: None

    def bind_ui(self, log_fn, action_fn, status_fn):
        self._log = log_fn
        self._action = action_fn
        self._status = status_fn

    def _reply(self, text):
        self.speaker.say(text)
        self._log("beaver", text)

    def _embed(self, mode, url, title):
        self._action({"type": "embed", "mode": mode, "url": url, "title": title})

    def _card(self, title, body):
        self._action({"type": "card", "title": title, "body": body})

    def handle(self, text):
        text = (text or "").strip().lower()
        if not text:
            return
        for matcher, action in self._routes():
            m = matcher(text)
            if m is not None:
                action(m if isinstance(m, str) else text)
                return
        self._web_search(text)

    def _routes(self):
        def kw(*words):
            def f(t):
                return t if any(w in t for w in words) else None
            return f

        def after(prefix):
            def f(t):
                m = re.search(prefix + r"\s+(.*)", t)
                return m.group(1).strip() if m else None
            return f

        return [
            (after(r"(?:show me|open|find|navigate to|directions to)\s+(?:maps?\s+(?:of|for|to)?|map\s+(?:of|for|to)?)"), self._maps),
            (kw("map", "maps", "directions", "navigate"), self._maps_generic),
            (after(r"(?:play|search youtube for|youtube)"), self._video),
            (kw("youtube", "video"), self._video_generic),
            (after(r"(?:what's the weather|weather in|weather for|weather)"), self._weather),
            (kw("weather", "forecast", "temperature"), self._weather_generic),
            (after(r"(?:tell me about|wikipedia|wiki|who is|what is)"), self._wiki),
            (after(r"(?:search for|search|look up|google)"), self._web_search),
            (kw("news", "headlines"), self._news),
            (kw("time", "clock"), self._time),
            (kw("date", "day", "today"), self._date),
            (after(r"(?:open|launch|start)"), self._open_app),
            (kw("clear", "close panel", "dismiss"), self._clear),
            (kw("hello", "hi ", "hey"), self._greet),
            (kw("thank"), self._thanks),
            (kw("who are you", "your name"), self._whoami),
        ]

    def _maps(self, place):
        place = place.strip()
        if not place:
            return self._maps_generic("")
        q = urllib.parse.quote(place)
        embed = f"https://maps.google.com/maps?q={q}&output=embed"
        self._reply(f"Showing maps for {place}.")
        self._embed("map", embed, f"Map · {place}")

    def _maps_generic(self, _):
        embed = "https://maps.google.com/maps?q=&output=embed"
        self._reply("Opening maps.")
        self._embed("map", embed, "Maps")

    def _video(self, query):
        query = query.strip()
        if not query:
            return self._video_generic("")
        q = urllib.parse.quote(query)
        embed = f"https://www.youtube.com/embed?listType=search&list={q}"
        self._reply(f"Playing {query}.")
        self._embed("video", embed, f"Video · {query}")

    def _video_generic(self, _):
        self._reply("Opening YouTube.")
        self._embed("web", "https://www.youtube.com", "YouTube")

    def _weather(self, city):
        city = (city or "").strip()
        target = city or "your area"
        q = urllib.parse.quote(city) if city else ""
        self._reply(f"Here's the weather for {target}.")
        self._embed("web", f"https://wttr.in/{q}", f"Weather · {target}")

    def _weather_generic(self, _):
        self._weather("")

    def _wiki(self, topic):
        topic = (topic or "").strip()
        if not topic:
            return self._web_search("")
        q = urllib.parse.quote(topic.replace(" ", "_"))
        url = f"https://en.wikipedia.org/wiki/{q}"
        self._reply(f"Here's what I found on {topic}.")
        self._embed("web", url, f"Wiki · {topic}")

    def _news(self, _):
        self._reply("Here are the latest headlines.")
        self._embed("web", "https://news.google.com", "News")

    def _web_search(self, query):
        query = query.strip()
        if not query:
            self._reply("What would you like me to search for?")
            return
        q = urllib.parse.quote(query)
        url = f"https://duckduckgo.com/?q={q}&ia=web"
        self._reply(f"Searching for {query}.")
        self._embed("web", url, f"Search · {query}")

    def _time(self, _):
        now = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
        self._reply(f"It's {now}.")
        self._card("CURRENT TIME", now)

    def _date(self, _):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self._reply(f"Today is {today}.")
        self._card("TODAY", today)

    def _open_app(self, name):
        name = (name or "").strip()
        if not name:
            self._reply("Which app should I open?")
            return
        web_apps = {
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "maps": "https://www.google.com/maps",
            "github": "https://github.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "twitter": "https://twitter.com",
            "reddit": "https://www.reddit.com",
            "calendar": "https://calendar.google.com",
        }
        for key, url in web_apps.items():
            if key in name:
                self._reply(f"Opening {key}.")
                self._embed("web", url, key.title())
                return

        native = {
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "file explorer": "explorer",
            "explorer": "explorer",
            "settings": "start ms-settings:",
            "camera": "start microsoft.windows.camera:",
            "command prompt": "cmd",
            "cmd": "cmd",
            "task manager": "taskmgr",
        }
        if platform.system() == "Windows":
            for key, cmd in native.items():
                if key in name:
                    try:
                        subprocess.Popen(cmd, shell=True)
                        self._reply(f"Opening {key}.")
                        self._card("LAUNCHED", key.title())
                        return
                    except Exception:
                        self._reply(f"I couldn't open {key}.")
                        return

        self._reply(f"I couldn't find an app called {name}, searching the web.")
        self._web_search(name)

    def _clear(self, _):
        self._action({"type": "clear"})
        self._reply("Cleared.")

    def _greet(self, _):
        self._reply("Hey there. I'm listening.")

    def _thanks(self, _):
        self._reply("Anytime.")

    def _whoami(self, _):
        self._reply("I'm Beaver, your local voice assistant. Everything runs on your machine.")
