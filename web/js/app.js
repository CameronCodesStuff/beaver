const $ = (id) => document.getElementById(id);

const micBtn = $("micBtn");
const stopBtn = $("stopBtn");
const sendBtn = $("sendBtn");
const textInput = $("textInput");
const orb = $("orb");
const bars = $("bars");
const subtitle = $("subtitle");
const statusText = $("statusText");
const statusDot = $("statusDot");
const logEl = $("log");
const vpBody = $("vpBody");
const vpTitle = $("vpTitle");
const vpClose = $("vpClose");
const chipsEl = $("chips");
const wakeHint = $("wakeHint");
const toneChip = $("toneChip");
const toneEmoji = $("toneEmoji");
const toneLabel = $("toneLabel");

const overlay = $("overlay");
const overlaySub = $("overlaySub");
const modelChoice = $("modelChoice");
const installSmall = $("installSmall");
const installLarge = $("installLarge");
const enterBtn = $("enterBtn");
const progressWrap = $("progressWrap");
const progressFill = $("progressFill");
const progressLabel = $("progressLabel");

let live = false;

for (let i = 0; i < 11; i++) {
  const s = document.createElement("span");
  s.style.animationDelay = (i * 0.06) + "s";
  bars.appendChild(s);
}

const SUGGESTIONS = [
  "what apps are open",
  "research electric cars",
  "recent files",
  "current tab",
  "play lofi beats",
  "weather in London",
  "go to github",
  "what time is it",
];
SUGGESTIONS.forEach((s) => {
  const c = document.createElement("div");
  c.className = "chip";
  c.textContent = s;
  c.onclick = () => runText(s);
  chipsEl.appendChild(c);
});

micBtn.onclick = async () => {
  const res = await eel.start_listening()();
  if (res && res.ok) {
    setLive(true);
  } else if (res && res.error === "model_missing") {
    showOverlay(true);
  } else if (res && res.message) {
    setSubtitle(res.message, false);
  }
};

stopBtn.onclick = async () => {
  await eel.stop_listening()();
  setLive(false);
};

sendBtn.onclick = () => {
  const v = textInput.value.trim();
  if (v) runText(v);
};
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

vpClose.onclick = clearViewport;

let miniOn = false;
const miniBtn = $("miniBtn");
const hushBtn = $("hushBtn");

miniBtn.onclick = async () => {
  miniOn = !miniOn;
  document.body.classList.toggle("mini", miniOn);
  miniBtn.classList.toggle("active", miniOn);
  try {
    const res = await eel.toggle_mini(miniOn)();
    if (miniOn && res && res.ok === false) {
      setSubtitle("Compact view on. (Couldn't pin the window on top automatically.)", false);
    }
  } catch {}
};

hushBtn.onclick = () => {
  try { eel.stop_speaking()(); } catch {}
};

function runText(text) {
  textInput.value = "";
  eel.send_text_command(text)();
}

function setLive(on) {
  live = on;
  micBtn.classList.toggle("live", on);
  micBtn.textContent = on ? "◉ LISTENING" : "▶ WAKE BEAVER";
  micBtn.disabled = on;
  stopBtn.disabled = !on;
  orb.classList.toggle("active", on);
  statusDot.classList.toggle("live", on);
}

function setSubtitle(text, isYou) {
  subtitle.innerHTML = "";
  subtitle.textContent = text;
  subtitle.classList.toggle("you", !!isYou);
}

eel.expose(setStatus);
function setStatus(text) {
  statusText.textContent = text;
  if (text === "LISTENING") setLive(true);
  if (text === "STANDBY") setLive(false);
}

eel.expose(setPartial);
function setPartial(text) {
  if (!text) return;
  setSubtitle("“" + text + "”", true);
}

eel.expose(addLog);
function addLog(role, text) {
  const line = document.createElement("div");
  line.className = "log-line " + role;
  const who = document.createElement("span");
  who.className = "who";
  who.textContent = role === "beaver" ? "BEAVER" : role === "user" ? "YOU" : "SYS";
  const msg = document.createElement("span");
  msg.className = "msg";
  msg.textContent = text;
  line.appendChild(who);
  line.appendChild(msg);
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
  if (role === "beaver") flashSpeak();
}

eel.expose(fireAction);
function fireAction(json) {
  let a;
  try { a = JSON.parse(json); } catch { return; }
  if (a.type === "clear") return clearViewport();
  if (a.type === "embed") return embed(a.mode, a.url, a.title);
  if (a.type === "card") return showCard(a.title, a.body);
  if (a.type === "list") return showList(a.title, a.items);
  if (a.type === "tone") return showTone(a.tone, a.emoji, a.confidence);
  if (a.type === "research_progress") return showResearchProgress(a.message);
  if (a.type === "report") return showReport(a.title, a.markdown, a.path);
  if (a.type === "building") return showBuilding(a.message);
  if (a.type === "site") return showSite(a.title, a.html, a.path);
  if (a.type === "needs_key") return showNeedsKey();
}

function showBuilding(msg) {
  vpTitle.textContent = "BUILDING";
  vpBody.innerHTML =
    '<div class="vp-research"><div class="spinner"></div><p>' + esc(msg || "Building…") + "</p></div>";
}

function showSite(title, html, path) {
  vpTitle.textContent = (title || "SITE").toUpperCase();
  vpBody.innerHTML = "";
  const frame = document.createElement("iframe");
  frame.srcdoc = html;
  frame.sandbox = "allow-scripts allow-forms allow-modals allow-popups";
  vpBody.appendChild(frame);
  if (path) {
    const bar = document.createElement("div");
    bar.className = "site-bar";
    bar.textContent = "Saved: " + path + "  ·  Say what to change and I'll update it";
    vpBody.appendChild(bar);
  }
}

function showNeedsKey() {
  vpTitle.textContent = "API KEY NEEDED";
  vpBody.innerHTML =
    '<div class="vp-keynote"><h3>To build sites, add an API key</h3>' +
    '<p>Create a file named <code>api_key.txt</code> in the Beaver folder and paste your ' +
    'Anthropic API key inside it. Then ask me to build again.</p>' +
    '<p>Get a key at <span class="kacc">console.anthropic.com</span></p></div>';
}

function showList(title, items) {
  vpTitle.textContent = (title || "LIST").toUpperCase();
  let html = '<div class="vp-list"><ul>';
  (items || []).forEach((it) => { html += "<li>" + esc(it) + "</li>"; });
  html += "</ul></div>";
  vpBody.innerHTML = html;
}

function showTone(tone, emoji, confidence) {
  toneChip.hidden = false;
  toneEmoji.textContent = emoji || "🙂";
  toneLabel.textContent = (tone || "neutral").toUpperCase();
  toneChip.className = "tone-chip tone-" + (tone || "neutral");
}

function showResearchProgress(msg) {
  vpTitle.textContent = "RESEARCHING";
  vpBody.innerHTML =
    '<div class="vp-research"><div class="spinner"></div><p>' + esc(msg) + "</p></div>";
}

function showReport(title, markdown, path) {
  vpTitle.textContent = (title || "REPORT").toUpperCase();
  const wrap = document.createElement("div");
  wrap.className = "vp-report";
  wrap.innerHTML = renderMarkdown(markdown);
  if (path) {
    const note = document.createElement("p");
    note.className = "report-saved";
    note.textContent = "Saved to: " + path;
    wrap.appendChild(note);
  }
  vpBody.innerHTML = "";
  vpBody.appendChild(wrap);
}

function renderMarkdown(md) {
  let h = esc(md);
  h = h.replace(/^### (.*)$/gm, "<h3>$1</h3>");
  h = h.replace(/^## (.*)$/gm, "<h2>$1</h2>");
  h = h.replace(/^# (.*)$/gm, "<h1>$1</h1>");
  h = h.replace(/\*(.*?)\*/g, "<em>$1</em>");
  h = h.replace(/&lt;(https?:\/\/[^&]+)&gt;/g, '<a href="$1" target="_blank">$1</a>');
  h = h.replace(/\n{2,}/g, "</p><p>");
  h = h.replace(/\n/g, "<br>");
  return "<p>" + h + "</p>";
}

function embed(mode, url, title) {
  vpTitle.textContent = (title || "VIEWPORT").toUpperCase();
  vpBody.innerHTML = "";
  const frame = document.createElement("iframe");
  frame.src = url;
  frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; geolocation";
  frame.referrerPolicy = "no-referrer-when-downgrade";
  vpBody.appendChild(frame);
}

function showCard(title, body) {
  vpTitle.textContent = "VIEWPORT";
  vpBody.innerHTML =
    '<div class="vp-card"><div class="vc-title">' + esc(title) +
    '</div><div class="vc-body">' + esc(body) + "</div></div>";
}

function clearViewport() {
  vpTitle.textContent = "VIEWPORT";
  vpBody.innerHTML =
    '<div class="vp-idle"><img src="assets/beaver.png" class="vp-idle-logo" alt=""><p>Maps, video, weather, and search appear here.</p></div>';
}

function flashSpeak() {
  orb.classList.add("speak");
  statusDot.classList.add("speaking");
  setTimeout(() => {
    orb.classList.remove("speak");
    statusDot.classList.remove("speaking");
  }, 1200);
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

/* ---------- install / first-run flow ---------- */
function showOverlay(forceInstall) {
  overlay.classList.remove("hidden");
  if (forceInstall) {
    overlaySub.textContent = "Choose a voice model to install.";
    modelChoice.hidden = false;
    enterBtn.hidden = true;
  }
}

function startInstall(large) {
  modelChoice.hidden = true;
  progressWrap.hidden = false;
  overlaySub.textContent = large
    ? "Installing the accurate model (large download)…"
    : "Installing the fast model…";
  eel.install_model(large)();
}

installSmall.onclick = () => startInstall(false);
installLarge.onclick = () => startInstall(true);

enterBtn.onclick = () => {
  overlay.classList.add("hidden");
};

eel.expose(installProgress);
function installProgress(pct, msg) {
  if (pct < 0) {
    overlaySub.textContent = msg + " — you can retry.";
    modelChoice.hidden = false;
    progressWrap.hidden = true;
    return;
  }
  progressFill.style.width = pct + "%";
  progressLabel.textContent = msg || pct + "%";
}

eel.expose(installDone);
function installDone(ok) {
  if (ok) {
    progressFill.style.width = "100%";
    progressLabel.textContent = "Done!";
    overlaySub.textContent = "Voice model installed. You're ready.";
    enterBtn.hidden = false;
  } else {
    overlaySub.textContent = "Install failed. Check your connection and retry.";
    modelChoice.hidden = false;
    progressWrap.hidden = true;
  }
}

/* ---------- boot ---------- */
(async () => {
  try {
    const w = await eel.get_wake_word()();
    if (w) wakeHint.textContent = w;
  } catch {}

  try {
    const st = await eel.model_status()();
    if (st && st.ready) {
      overlaySub.textContent = "Voice model ready.";
      enterBtn.hidden = false;
      modelChoice.hidden = true;
      progressWrap.hidden = true;
    } else {
      showOverlay(true);
    }
  } catch {
    showOverlay(true);
  }
})();
