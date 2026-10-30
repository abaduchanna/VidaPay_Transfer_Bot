"""update_checker.py — 3SVerse auto-update prompt for Windows builds.

Safe by design (never breaks the app):
  * Only active in frozen (PyInstaller) builds — dev runs are no-ops.
  * Every step wrapped; ANY failure = silent no-op, retry next day.
  * Background daemon thread; the dialog runs on the Tk main thread.
  * Source: public GitHub release assets (3SVerse_Downloads mirror or the
    app's own public repo). No tokens baked in, 1 check per day per app.

Update signal: release asset ``updated_at`` fingerprint (rolling "latest"
mirror). Installed app stores the fingerprint it shipped with; when the
asset changes, a new build is available.

Install: downloads to %TEMP%, verifies MZ header, then a small .bat waits
for this process to exit, swaps the exe (with rollback on copy failure)
and restarts the app. License files (%APPDATA%) are untouched.
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time

_GITHUB_API = "https://api.github.com/repos/{repo}/releases{tag_path}"
_GITHUB_DL = "https://github.com/{repo}/releases/latest/download/{asset}"
_CHECK_INTERVAL = 24 * 3600          # one check per day
_API_TIMEOUT = 20
_DL_TIMEOUT = 120
_MIN_BYTES = 300_000                 # sanity floor for a real exe
_MAX_WAIT_EXIT_S = 30                # updater bat waits max this long

_CREATE_NO_WINDOW = 0x08000000


def _state_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, ".3sv_updates")


def _state_path(app_id):
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in app_id)
    return os.path.join(_state_dir(), safe + ".json")


def _load_state(app_id):
    try:
        with open(_state_path(app_id), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(app_id, state):
    try:
        os.makedirs(_state_dir(), exist_ok=True)
        with open(_state_path(app_id), "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


def _fetch_latest_asset(repo, tag, asset_name):
    """Return {'fp','url','size'} via api.github.com. Never raises.
    Primary path is _fetch_fingerprint (CDN HEAD, no rate limits); this is
    the fallback when HEAD is blocked but the API is not."""
    import urllib.request

    try:
        tag_path = "/tags/" + tag if tag else "/latest"
        url = _GITHUB_API.format(repo=repo, tag_path=tag_path)
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "3SVerse-UpdateChecker/1.0")
        req.add_header("Accept", "application/vnd.github+json")
        with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
        for a in data.get("assets") or []:
            if a.get("name") == asset_name:
                dl = "https://github.com/{repo}/releases/download/{t}/{a}".format(
                    repo=repo, t=data.get("tag_name") or tag or "latest",
                    a=asset_name)
                return {"fp": a.get("updated_at") or "", "url": dl,
                        "size": int(a.get("size") or 0)}
    except Exception:
        pass
    return None


def _fetch_fingerprint(repo, asset_name):
    """Return {'fp','url','size'} via a CDN HEAD request on the stable
    /releases/latest/download/ URL. No api.github.com => no rate limit.
    Never raises."""
    import urllib.request

    try:
        url = _GITHUB_DL.format(repo=repo, asset=asset_name)
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "3SVerse-UpdateChecker/1.0")
        with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as r:
            if r.status != 200:
                return None
            fp = r.headers.get("Last-Modified") or r.headers.get("ETag")
            if not fp:
                return None
            try:
                size = int(r.headers.get("Content-Length") or 0)
            except Exception:
                size = 0
            return {"fp": fp, "url": url, "size": size}   # stable URL (redirect expires)
    except Exception:
        pass
    return None


def _download(url, dest_path, attempts=3):
    """Hardened single-stream download - a half-fetched update can never
    install. Streams to <dest>.part, verifies the byte count against
    Content-Length (a truncated/snatched .part is the #1 failure mode -
    AV and cleanup tools grab freshly written files mid-stream), resumes
    an interrupted attempt via a Range request when possible, and retries
    whatever fails. MZ magic is re-checked on every attempt."""
    import urllib.request

    last_err = None
    for attempt in range(1, max(1, attempts) + 1):
        part = dest_path + ".part"
        try:
            offset = 0
            if attempt > 1 and os.path.exists(part):
                try:
                    offset = os.path.getsize(part)
                except Exception:
                    offset = 0
                if offset < _MIN_BYTES:
                    offset = 0
            headers = {"User-Agent": "3SVerse-UpdateChecker/1.0"}
            if offset:
                headers["Range"] = "bytes=%d-" % offset
            req = urllib.request.Request(url, headers=headers)
            expected = 0
            with urllib.request.urlopen(req, timeout=_DL_TIMEOUT) as r:
                if offset and r.status != 206:
                    offset = 0        # server ignored Range - restart clean
                try:
                    expected = int(r.headers.get("Content-Length") or 0)
                except Exception:
                    expected = 0
                with open(part, "ab" if offset else "wb") as f:
                    while True:
                        chunk = r.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
            size = os.path.getsize(part) if os.path.exists(part) else 0
            got = size - offset
            if expected and got != expected:
                raise ValueError("truncated download (%d of %d bytes)"
                                 % (got, expected))
            if size < _MIN_BYTES:
                raise ValueError("download too small")
            os.replace(part, dest_path)
            with open(dest_path, "rb") as f:
                if f.read(2) != b"MZ":
                    raise ValueError("not a Windows exe")
            return dest_path
        except Exception as e:
            last_err = e
            if attempt >= max(1, attempts):
                break
            time.sleep(1.0)
    try:
        if os.path.exists(dest_path + ".part"):
            os.remove(dest_path + ".part")
    except Exception:
        pass
    raise last_err if last_err else OSError("download failed")


def _updater_bat_text(exe_path, new_path):
    exe_name = os.path.basename(exe_path)
    return "\r\n".join([
        "@echo off",
        "setlocal enabledelayedexpansion",
        'set "EXE=' + exe_name + '"',
        "set /a tries=0",
        ":waitloop",
        'tasklist /FI "IMAGENAME eq %EXE%" 2>nul | find /I "%EXE%" >nul',
        "if not errorlevel 1 (",
        "  set /a tries+=1",
        "  if !tries! GEQ " + str(_MAX_WAIT_EXIT_S) + " goto force",
        '  timeout /t 1 /nobreak >nul',
        "  goto waitloop",
        ")",
        "goto swap",
        ":force",
        'taskkill /F /IM %EXE% >nul 2>&1',
        'timeout /t 2 /nobreak >nul',
        ":swap",
        'move /y "' + exe_path + '" "' + exe_path + '.old" >nul 2>&1',
        'copy /y "' + new_path + '" "' + exe_path + '" >nul 2>&1',
        "if errorlevel 1 (",
        '  move /y "' + exe_path + '.old" "' + exe_path + '" >nul 2>&1',
        ") else (",
        '  start "" "' + exe_path + '"',
        '  del /f /q "' + exe_path + '.old" >nul 2>&1',
        ")",
        'del /f /q "' + new_path + '" >nul 2>&1',
        'del /f /q "%~f0" >nul 2>&1',
        "",
    ])


def _apply_update(exe_path, new_path, root):
    """Write + launch the updater bat, then let this process exit."""
    bat_path = os.path.join(tempfile.gettempdir(),
                            "update_" + os.path.basename(exe_path) + ".bat")
    enc = "mbcs" if os.name == "nt" else "utf-8"
    try:
        with open(bat_path, "w", encoding=enc, errors="replace") as f:
            f.write(_updater_bat_text(exe_path, new_path))
    except LookupError:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(_updater_bat_text(exe_path, new_path))
    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = _CREATE_NO_WINDOW
    subprocess.Popen([bat_path], close_fds=True, **kwargs)
    try:
        root.after(120, os._exit, 0)
    except Exception:
        os._exit(0)


def _remember(app_id, key, value):
    state = _load_state(app_id)
    state[key] = value
    _save_state(app_id, state)


def _ask_download(root, app_id, repo, tag, asset_name, fp, url, exe_path):
    """Runs on the Tk main thread: offer the update, then download."""
    try:
        import tkinter.messagebox as mb
        yes = mb.askyesno(
            "3SVerse — Update available",
            "A new version of this app is available"
            + _pretty_date(fp) + ".\n\nDownload and install it now?",
            parent=root)
        if not yes:
            _remember(app_id, "skip", fp)    # declined — don't ask again for this build
            return
        new_path = os.path.join(tempfile.gettempdir(),
                                app_id.replace(" ", "_") + ".update.exe")
        _download(url, new_path)
        _ask_and_apply(root, exe_path, new_path, app_id, fp)
    except Exception:
        pass


def _ask_and_apply(root, exe_path, new_path, app_id, fp):
    """Runs on the Tk main thread via root.after."""
    try:
        import tkinter.messagebox as mb
        yes = mb.askyesno(
            "3SVerse — Update ready",
            "The new version is downloaded and ready.\n\n"
            "Restart the app now to install it?",
            parent=root)
        if yes:
            _remember(app_id, "fp", fp)      # after restart, check stays silent
            _apply_update(exe_path, new_path, root)
        else:
            try:
                os.remove(new_path)
            except Exception:
                pass
    except Exception:
        pass


def _pretty_date(fp):
    try:
        return " (published " + str(fp).strip()[:16] + ")"
    except Exception:
        return ""


def _worker(root, app_id, repo, tag, asset_name, delay):
    try:
        time.sleep(delay)
        if not getattr(sys, "frozen", False):
            return                       # dev run — never self-update
        exe_path = getattr(sys, "executable", "")
        if not exe_path or not exe_path.lower().endswith(".exe"):
            return
        state = _load_state(app_id)
        now = time.time()
        if now - float(state.get("last_check", 0)) < _CHECK_INTERVAL:
            return

        info = _fetch_fingerprint(repo, asset_name)      # CDN HEAD (no rate limit)
        if not info:
            info = _fetch_latest_asset(repo, tag, asset_name)  # API fallback
        state["last_check"] = now
        _save_state(app_id, state)
        if not info:
            return
        fp, url, size = info["fp"], info["url"], info.get("size") or 0
        if not fp or not url:
            return
        if state.get("fp") == fp or state.get("skip") == fp:
            return                       # already on (or declined) this build
        if not state.get("fp") and size:
            try:
                if os.path.getsize(exe_path) == size:
                    state["fp"] = fp     # fresh install of exactly this build
                    _save_state(app_id, state)
                    return
            except Exception:
                pass

        try:
            root.winfo_exists()
        except Exception:
            return
        root.after(0, _ask_download, root, app_id, repo, tag,
                   asset_name, fp, url, exe_path)
    except Exception:
        pass                             # never break the app


def check_async(root, app_id, repo, asset_name, tag="latest", delay=25):
    """Call once at startup. Silent no-op on any error / dev machines."""
    try:
        t = threading.Thread(
            target=_worker,
            args=(root, app_id, repo, tag, asset_name, delay),
            daemon=True)
        t.start()
    except Exception:
        pass
