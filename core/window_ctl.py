import os
import platform

# The Chrome/Edge app window carries the page <title>.
APP_TITLE_MATCH = "Voice Assistant"        # specific to Beaver's page title
FALLBACK_TITLE_MATCH = "localhost:8000"    # if shown by URL instead

# Window classes we must never pin (these are File Explorer / shell windows)
BAD_CLASSES = {
    "CabinetWClass", "ExploreWClass", "Progman", "WorkerW", "Shell_TrayWnd",
}
# Browser window classes that Eel's app window uses
GOOD_CLASSES = {
    "Chrome_WidgetWin_1",   # Chrome / Edge / Brave (Chromium)
    "MozillaWindowClass",   # Firefox
}


def _find_window():
    try:
        import win32gui
    except Exception:
        return None

    matches = []

    def cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        cls = win32gui.GetClassName(hwnd) or ""
        if cls in BAD_CLASSES:
            return
        title_ok = (APP_TITLE_MATCH in title) or (FALLBACK_TITLE_MATCH in title)
        if not title_ok:
            return
        # Strongly prefer real browser windows; rank by class quality
        rank = 0 if cls in GOOD_CLASSES else 1
        matches.append((rank, hwnd, title, cls))

    try:
        win32gui.EnumWindows(cb, None)
    except Exception:
        return None

    if not matches:
        return None
    matches.sort(key=lambda m: m[0])  # good classes first
    return matches[0][1]


def set_mini(enabled, width=380, height=560, margin=20):
    """Pin the Beaver app window on top, docked bottom-right (enabled=True),
    or restore normal stacking (enabled=False). Windows only.
    Returns True only if the genuine Beaver window was found and moved."""
    if platform.system() != "Windows":
        return False
    try:
        import win32gui
        import win32con
        import ctypes
    except Exception:
        return False

    hwnd = _find_window()
    if not hwnd:
        return False

    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)

    if enabled:
        x = screen_w - width - margin
        y = screen_h - height - margin - 48  # leave room above the taskbar
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST, x, y, width, height,
            win32con.SWP_SHOWWINDOW,
        )
    else:
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
        )
    return True
