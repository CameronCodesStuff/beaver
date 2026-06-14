import os
import platform
import subprocess

from core import config


def running_apps():
    apps = []
    if platform.system() == "Windows":
        try:
            import psutil
            seen = set()
            for p in psutil.process_iter(["name"]):
                n = (p.info["name"] or "").replace(".exe", "")
                if n and n.lower() not in seen and _is_user_app(n):
                    seen.add(n.lower())
                    apps.append(n)
        except Exception:
            apps = _tasklist_fallback()
    else:
        try:
            out = subprocess.check_output(["ps", "-eo", "comm"], text=True)
            apps = sorted(set(l.strip() for l in out.splitlines()[1:] if l.strip()))[:40]
        except Exception:
            apps = []
    return sorted(apps)[:40]


def _tasklist_fallback():
    try:
        out = subprocess.check_output("tasklist /fo csv /nh", shell=True, text=True)
        names = set()
        for line in out.splitlines():
            parts = line.split('","')
            if parts:
                n = parts[0].strip('"').replace(".exe", "")
                if _is_user_app(n):
                    names.add(n)
        return sorted(names)
    except Exception:
        return []


def _is_user_app(name):
    junk = {
        "svchost", "system", "registry", "csrss", "wininit", "services",
        "lsass", "smss", "dwm", "fontdrvhost", "spoolsv", "conhost",
        "runtimebroker", "sihost", "taskhostw", "ctfmon", "searchhost",
        "shellexperiencehost", "startmenuexperiencehost", "textinputhost",
        "backgroundtaskhost", "wmiprvse", "audiodg", "memcompression",
        "idle", "secure system", "registry",
    }
    return name.lower() not in junk and not name.lower().startswith("microsoft.")


def open_windows():
    titles = []
    if platform.system() == "Windows":
        try:
            import win32gui
            def cb(hwnd, acc):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if t and len(t) > 1:
                        acc.append(t)
            win32gui.EnumWindows(cb, titles)
        except Exception:
            pass
    return titles[:30]


def active_browser_tab():
    if platform.system() != "Windows":
        return None
    try:
        import win32gui
        title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except Exception:
        return None
    for sep in [" - Google Chrome", " - Microsoft\u200b Edge", " - Microsoft Edge",
                " — Mozilla Firefox", " - Mozilla Firefox", " - Brave", " - Opera"]:
        if sep in title:
            return title.replace(sep, "").strip()
    return None


def recent_files(limit=15):
    folders = []
    home = os.path.expanduser("~")
    for sub in config.SCAN_FOLDERS:
        path = os.path.join(home, sub)
        if os.path.isdir(path):
            folders.append(path)

    items = []
    for folder in folders:
        try:
            for entry in os.scandir(folder):
                if entry.is_file():
                    try:
                        items.append((entry.path, entry.stat().st_mtime))
                    except OSError:
                        pass
        except OSError:
            pass

    items.sort(key=lambda x: x[1], reverse=True)
    return [os.path.basename(p) for p, _ in items[:limit]]
