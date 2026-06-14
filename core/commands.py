import re
import json
import datetime
import urllib.parse
import urllib.request
import subprocess
import platform

try:
    from core import system_info
except Exception:
    system_info = None
try:
    from core import tone
except Exception:
    tone = None
try:
    from core import research
except Exception:
    research = None
try:
    from core import generator
except Exception:
    generator = None


class CommandRouter:
    def __init__(self, speaker):
        self.speaker = speaker
        self._log = lambda role, text: None
        self._action = lambda action: None
        self._status = lambda text: None
        self._current_tone = "neutral"
        self._gen_history = None
        self._gen_name = "site"
        self._awaiting_gen_edit = False

    def bind_ui(self, log_fn, action_fn, status_fn):
        self._log = log_fn
        self._action = action_fn
        self._status = status_fn

    def _reply(self, text, adapt=True):
        if adapt and tone is not None and self._current_tone != "neutral":
            try:
                text = tone.adapt(self._current_tone, text)
            except Exception:
                pass
        self.speaker.say(text)
        self._log("beaver", text)

    def _embed(self, mode, url, title):
        self._action({"type": "embed", "mode": mode, "url": url, "title": title})

    def _card(self, title, body):
        self._action({"type": "card", "title": title, "body": body})

    def _list_card(self, title, items):
        self._action({"type": "list", "title": title, "items": items})

    def handle(self, text):
        raw = (text or "").strip()
        text = raw.lower()
        if not text:
            return
        if tone is not None:
            try:
                t, conf = tone.detect(text)
                self._current_tone = t
                self._action({"type": "tone", "tone": t, "emoji": tone.emoji(t), "confidence": conf})
            except Exception:
                self._current_tone = "neutral"

        # If we just built a site and the user is giving a follow-up edit,
        # route it back to the generator instead of normal commands.
        if self._awaiting_gen_edit and self._is_edit_request(text):
            self._generate(raw, is_edit=True)
            return

        for matcher, action in self._routes():
            try:
                m = matcher(text)
            except Exception:
                continue
            if m is not None:
                self._awaiting_gen_edit = (action == self._generate)
                try:
                    if action == self._generate:
                        action(raw)
                    else:
                        action(m if isinstance(m, str) else text)
                except Exception:
                    self._reply("Sorry, that command ran into an error.", adapt=False)
                return
        self._web_search(text)

    def _is_edit_request(self, text):
        # Heuristics: short imperative tweaks like "make it blue", "add a button",
        # "change the title", "now make it darker". Avoid hijacking new commands.
        if any(text.startswith(w) for w in ("make ", "change ", "add ", "remove ",
                "now ", "also ", "set ", "use ", "put ", "move ", "turn ", "give it",
                "can you make", "instead")):
            return True
        edit_words = ("bigger", "smaller", "darker", "lighter", "color", "colour",
                      "background", "font", "button", "title", "header", "footer")
        return any(w in text for w in edit_words)

    def _routes(self):
        def kw(*words):
            pats = [re.compile(r"\b" + re.escape(w) + r"\b") for w in words]
            def f(t):
                return t if any(p.search(t) for p in pats) else None
            return f

        def after(prefix):
            def f(t):
                m = re.search(prefix + r"\s+(.*)", t)
                return m.group(1).strip() if m else None
            return f

        def after0(prefix):
            # like after() but the tail may be empty
            def f(t):
                m = re.search(prefix + r"\b\s*(.*)", t)
                return m.group(1).strip() if m else None
            return f

        return [
            (after0(r"(?:generate|create|make|build|design|code|write)\s+(?:me\s+)?(?:a\s+|an\s+|the\s+)?(?:simple\s+|basic\s+|quick\s+|cool\s+)?(?:website|web page|webpage|web site|site|landing page|page|app|web app|game|html|portfolio|form|calculator|tool)"), self._generate),
            (after(r"(?:research|report on|compare sources|compare|generate a report on|write a report on)"), self._research),
            (kw("what apps are open", "what's running", "running apps", "open apps", "what programs"), self._apps),
            (kw("open windows", "what windows"), self._windows),
            (kw("what tab", "current tab", "browser tab", "what am i looking at"), self._tab),
            (kw("recent files", "my files", "what files", "current files"), self._files),
            (after(r"(?:directions to|show me maps?\s*(?:of|for|to|near|around|in)?|maps?\s+(?:of|for|to|near|around|in)|find\s+(?:the\s+)?maps?\s*(?:of|for|to)?)"), self._maps),
            (after(r"(?:go to|open website|open site|visit)"), self._navigate),
            (after(r"(?:what's the weather|weather in|weather for|weather)"), self._weather),
            (kw("weather", "forecast", "temperature"), self._weather_generic),
            (after(r"(?:play|search youtube for|youtube)"), self._video),
            (kw("youtube", "video"), self._video_generic),
            (kw("map", "maps", "directions"), self._maps_generic),
            (kw("news", "headlines"), self._news),
            (kw("time", "clock"), self._time),
            (kw("date", "today", "what day"), self._date),
            (after(r"(?:tell me about|wikipedia|wiki|who is|what is)"), self._wiki),
            (after(r"(?:search for|search|look up|google)"), self._web_search),
            (after(r"(?:navigate to)"), self._navigate),
            (after(r"(?:open|launch|start)"), self._open_app),
            (kw("how do you feel", "my mood", "how am i"), self._mood),
            (kw("clear", "dismiss"), self._clear),
            (kw("hello", "hey", "hi"), self._greet),
            (kw("thanks", "thank you"), self._thanks),
            (kw("who are you", "your name"), self._whoami),
        ]

    def _maps(self, place):
        place = (place or "").strip().strip("?.!,")
        place = re.sub(r"^(the|a|an)\s+", "", place)
        if not place or place in ("map", "maps"):
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
        self._reply(f"Playing {query}.")
        vid = self._youtube_first_id(query)
        if vid:
            embed = f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0"
            self._embed("video", embed, f"Video · {query}")
        else:
            q = urllib.parse.quote(query)
            self._embed("video", f"https://www.youtube-nocookie.com/embed?listType=search&list={q}", f"Video · {query}")

    def _youtube_first_id(self, query):
        try:
            q = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={q}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", "ignore")
            m = re.search(r'"videoId":"([\w-]{11})"', html)
            return m.group(1) if m else None
        except Exception:
            return None

    def _video_generic(self, _):
        self._reply("What would you like me to play?")

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
        self._reply("Opening the latest headlines in your browser.")
        self._open_external("https://news.google.com")
        self._card("NEWS", "Opened in browser")

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

        if "maps" in name:
            return self._maps_generic("")
        if "youtube" in name:
            self._reply("Opening YouTube. What would you like to watch?")
            self._embed("video", "https://www.youtube-nocookie.com/embed?listType=search&list=music", "YouTube")
            return

        external = {
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "twitter": "https://twitter.com",
            "reddit": "https://www.reddit.com",
            "calendar": "https://calendar.google.com",
        }
        for key, url in external.items():
            if key in name:
                self._reply(f"Opening {key} in your browser.")
                self._open_external(url)
                self._card("OPENED", key.title())
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

    def _apps(self, _):
        if system_info is None:
            self._reply("System info isn't available.")
            return
        apps = system_info.running_apps()
        if not apps:
            self._reply("I couldn't read the running apps.")
            return
        top = apps[:8]
        self._reply(f"You have {len(apps)} apps running, including {', '.join(top[:4])}.")
        self._list_card(f"RUNNING APPS · {len(apps)}", apps)

    def _windows(self, _):
        if system_info is None:
            self._reply("System info isn't available.")
            return
        wins = system_info.open_windows()
        if not wins:
            self._reply("I couldn't read the open windows.")
            return
        self._reply(f"You have {len(wins)} windows open.")
        self._list_card(f"OPEN WINDOWS · {len(wins)}", wins)

    def _tab(self, _):
        if system_info is None:
            self._reply("System info isn't available.")
            return
        tab = system_info.active_browser_tab()
        if tab:
            self._reply(f"Your active browser tab is: {tab}.")
            self._card("ACTIVE TAB", tab)
        else:
            self._reply("I don't see an active browser tab. Make sure a browser window is focused.")

    def _files(self, _):
        if system_info is None:
            self._reply("System info isn't available.")
            return
        files = system_info.recent_files()
        if not files:
            self._reply("I couldn't find any recent files in your folders.")
            return
        self._reply(f"Your most recent files include {', '.join(files[:3])}.")
        self._list_card(f"RECENT FILES · {len(files)}", files)

    def _navigate(self, target):
        target = (target or "").strip()
        if not target:
            self._reply("Where would you like to go?")
            return
        url = self._to_url(target)
        self._reply(f"Navigating to {target}.")
        self._embed("web", url, target)

    def _to_url(self, target):
        t = target.replace(" dot ", ".").replace(" ", "")
        if t.startswith("http"):
            return t
        if "." not in t:
            t = t + ".com"
        return "https://" + t

    def _research(self, query):
        if research is None:
            self._reply("Research isn't available right now.")
            return
        query = (query or "").strip()
        if not query:
            self._reply("What should I research?")
            return
        self._reply(f"Researching {query}. This may take a moment.")
        self._status("RESEARCHING")

        def progress(msg):
            self._action({"type": "research_progress", "message": msg})

        result, err = research.build_report(query, progress)
        self._status("LISTENING")
        if err:
            self._reply(f"Research failed: {err}")
            return
        n = len(result["sources"])
        self._reply(f"Done. I compared {n} sources and wrote a report.")
        self._action({
            "type": "report",
            "markdown": result["markdown"],
            "path": result["path"],
            "title": f"Report · {query}",
        })

    def _generate(self, prompt, is_edit=False):
        if generator is None:
            self._reply("The website generator isn't available.")
            return
        prompt = (prompt or "").strip()
        if not prompt:
            self._reply("What would you like me to build?")
            return

        if not generator.has_api_key():
            self._awaiting_gen_edit = False
            self._reply("To build sites I need an Anthropic API key. "
                        "Put your key in a file called api key dot txt in the Beaver folder, "
                        "then try again.")
            self._action({"type": "needs_key"})
            return

        if is_edit:
            self._reply("Updating it now.")
        else:
            self._reply("Building that now. Give me a moment.")
            self._gen_history = None
            self._gen_name = self._name_from_prompt(prompt)
        self._status("BUILDING")
        self._action({"type": "building", "message": "Generating your site…"})

        history = self._gen_history if is_edit else None
        html, result = generator.generate(prompt, history)
        self._status("LISTENING")

        if html is None:
            if result == "no_api_key":
                self._reply("I couldn't find a valid API key.")
            else:
                self._reply(f"Build failed: {result}")
            return

        self._gen_history = result
        self._awaiting_gen_edit = True
        path = generator.save(html, self._gen_name)
        self._reply("Done. It's showing in the viewport — test it, then just tell me "
                    "what to change and I'll update it.")
        self._action({
            "type": "site",
            "html": html,
            "path": path,
            "title": f"Site · {self._gen_name}",
        })

    def _name_from_prompt(self, prompt):
        words = re.sub(r"[^a-z0-9 ]", "", prompt.lower()).split()
        skip = {"a", "an", "the", "me", "simple", "basic", "quick", "website",
                "web", "page", "site", "app", "make", "build", "create",
                "generate", "design", "for", "of", "with", "called", "named"}
        keep = [w for w in words if w not in skip][:3]
        return "_".join(keep) or "site"

    def _mood(self, _):
        t = self._current_tone
        self._reply(f"You sound {t}." if t != "neutral" else "You sound steady and neutral.")
        emoji = tone.emoji(t) if tone is not None else "🙂"
        self._card("DETECTED MOOD", f"{emoji}  {t.title()}")

    def _open_external(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

    def _greet(self, _):
        self._reply("Hey there. I'm listening.")

    def _thanks(self, _):
        self._reply("Anytime.")

    def _whoami(self, _):
        self._reply("I'm Beaver, your local voice assistant. Everything runs on your machine.")
