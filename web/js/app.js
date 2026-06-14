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

const overlay = $("overlay");
const overlaySub = $("overlaySub");
const installBtn = $("installBtn");
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
  "open maps of Vancouver",
  "play lofi beats",
  "weather in London",
  "search for SpaceX",
  "tell me about beavers",
  "what time is it",
  "open calculator",
  "news",
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
    overlaySub.textContent = "The offline voice model isn't installed yet.";
    installBtn.hidden = false;
    enterBtn.hidden = true;
  }
}

installBtn.onclick = async () => {
  installBtn.hidden = true;
  progressWrap.hidden = false;
  overlaySub.textContent = "Installing the offline voice model…";
  await eel.install_model()();
};

enterBtn.onclick = () => {
  overlay.classList.add("hidden");
};

eel.expose(installProgress);
function installProgress(pct, msg) {
  if (pct < 0) {
    overlaySub.textContent = msg + " — you can retry.";
    installBtn.hidden = false;
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
    installBtn.hidden = false;
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
      installBtn.hidden = true;
      progressWrap.hidden = true;
    } else {
      showOverlay(true);
    }
  } catch {
    showOverlay(true);
  }
})();
