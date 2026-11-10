"""
Theme Manager - Standardized for GFH/VidaPay Ecosystem
Developed by www.3SVerse.com | Copyright © {year} | All rights reserved.
"""
import os

_THEME_MANAGER_VERSION = "2.1.0"
import json
from datetime import datetime

# ── Lazy tkinter import ──
# tkinter is imported inside methods that need it, not at module level.
# This prevents ModuleNotFoundError when the module is imported before
# tkinter availability is verified.


class ThemeManager:
    """Manages light/dark themes with protected widget tags."""


    BRAND_NAVY = "#090d26"
    BRAND_RED = "#f0541c"
    BRAND_WHITE = "#ffffff"

    THEMES = {
        "light": {
            "bg": "#f6f7fb",
            "panel": "#ffffff",
            "panel_alt": "#eef0f6",
            "text": "#16213a",
            "text_dim": "#5b6478",
            "input": "#ffffff",
            "border": "#d5d9e5",
            "navy": "#090d26",
            "red": "#f0541c",
            "log_bg": "#ffffff",
            "log_fg": "#16213a",
        },
        "dark": {
            "bg": "#0b1020",
            "panel": "#141b38",
            "panel_alt": "#1c2447",
            "text": "#e8ecf7",
            "text_dim": "#9aa4c0",
            "input": "#1c2447",
            "border": "#2b3561",
            "navy": "#090d26",
            "red": "#f0541c",
            "log_bg": "#05070f",
            "log_fg": "#cbd5e1",
        }
    }

    _PROTECTED_TAGS = {"header", "header_label", "brand", "logo", "run", "sched", "stop", "footer"}

    def __init__(self, default="dark", app_name="GFH"):
        self.app_name = app_name
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "gfh-telecom", app_name)
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "theme.json")
        self.current_theme = self._load_theme() or default
        os.makedirs(self.CONFIG_DIR, exist_ok=True)

    def _load_theme(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    return json.load(f).get("theme", "dark")
            except Exception:
                pass
        return None

    def save_theme(self, theme_name):
        self.current_theme = theme_name
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump({"theme": theme_name}, f)
        except Exception:
            pass

    def get_colors(self):
        return self.THEMES.get(self.current_theme, self.THEMES["dark"]).copy()

    def toggle(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.save_theme(self.current_theme)
        return self.current_theme

    def apply_theme_to_window(self, window):
        """Apply theme to a tkinter window."""
        import tkinter as tk
        from tkinter import ttk

        colors = self.get_colors()
        style = ttk.Style(window)
        style.theme_use("clam")

        # Configure ttk styles
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 9))
        style.configure("TCombobox", fieldbackground=colors.get("input", "#ffffff"), background=colors.get("panel_alt", "#eef0f6"), foreground=colors.get("text", "#16213a"))
        style.configure("TButton", background=colors["panel_alt"], foreground=colors["text"], font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground=colors["input"], foreground=colors["text"])
        style.configure("TNotebook", background=colors["bg"])
        style.configure("TNotebook.Tab", background=colors["panel_alt"], foreground=colors["text"], font=("Segoe UI", 9))
        style.map("TNotebook.Tab", background=[("selected", colors["panel"])])
        style.configure("Treeview", background=colors["panel"], foreground=colors["text"], fieldbackground=colors["panel"])
        style.configure("Treeview.Heading", background=self.BRAND_NAVY, foreground=self.BRAND_WHITE, font=("Segoe UI", 9, "bold"))
        style.map("Treeview.Heading", background=[("active", self.BRAND_NAVY)], foreground=[("active", self.BRAND_WHITE)])
        style.configure("Horizontal.TProgressbar", background=colors["red"], troughcolor=colors["panel_alt"])
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["text"])
        style.configure("TRadiobutton", background=colors["bg"], foreground=colors["text"])
        style.configure("TLabelframe", background=colors["bg"], foreground=colors["text"])
        style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 9, "bold"))

        window.configure(background=colors["bg"])
        self._walk(window, colors)

        # Keep Windows native chrome synchronized without changing this
        # partner app's own logo, icon, header, or background artwork.
        try:
            from native_titlebar import sync_titlebar
            sync_titlebar(window, dark=(self.current_theme == "dark"))
        except Exception:
            pass

    def _walk(self, widget, colors):
        """Walk widget tree and apply colors, skipping protected widgets."""
        import tkinter as tk

        for child in widget.winfo_children():
            # Skip ALL protected tags — header, footer, logo, etc.
            tag = getattr(child, "_tag", None)
            if tag in self._PROTECTED_TAGS:
                continue
            tags = set(child.bindtags())
            if tags & self._PROTECTED_TAGS:
                continue

            wtype = child.winfo_class()
            bg = colors["bg"]
            panel = colors.get("panel", colors["bg"])
            panel_alt = colors.get("panel_alt", colors["bg"])
            text_fg = colors["text"]
            input_bg = colors.get("input", panel)

            try:
                if wtype in ("Frame", "Tk", "Toplevel"):
                    child.configure(bg=bg)
                elif wtype in ("Labelframe", "labelframe", "TLabelframe"):
                    child.configure(bg=panel)
                elif wtype == "Label":
                    child.configure(bg=bg, fg=text_fg)
                elif wtype == "Button":
                    child.configure(bg=panel_alt, fg=text_fg,
                                    activebackground=panel,
                                    activeforeground=text_fg)
                elif wtype == "Entry":
                    child.configure(bg=input_bg, fg=text_fg,
                                    insertbackground=text_fg,
                                    disabledbackground=panel_alt)
                elif wtype == "Text":
                    child.configure(bg=panel, fg=text_fg,
                                    insertbackground=text_fg,
                                    selectbackground=colors.get("red", "#f0541c"),
                                    selectforeground="#ffffff")
                elif wtype == "Listbox":
                    child.configure(bg=input_bg, fg=text_fg,
                                    selectbackground=colors.get("red", "#f0541c"),
                                    selectforeground="#ffffff")
                elif wtype in ("Canvas", "canvas"):
                    child.configure(bg=bg, highlightbackground=colors.get("border", bg))
                elif wtype == "PanedWindow":
                    child.configure(bg=bg)
                elif wtype == "Checkbutton":
                    child.configure(bg=bg, fg=text_fg,
                                    activebackground=bg,
                                    activeforeground=text_fg,
                                    selectcolor=panel)
                elif wtype == "Radiobutton":
                    child.configure(bg=bg, fg=text_fg,
                                    activebackground=bg,
                                    activeforeground=text_fg,
                                    selectcolor=panel)
                elif wtype == "Scale":
                    child.configure(bg=bg, fg=text_fg,
                                    troughcolor=panel_alt,
                                    activebackground=colors.get("red", "#f0541c"))
                elif wtype == "Spinbox":
                    child.configure(bg=input_bg, fg=text_fg,
                                    insertbackground=text_fg,
                                    buttonbackground=panel_alt)
                elif wtype == "OptionMenu":
                    child.configure(bg=panel_alt, fg=text_fg,
                                    activebackground=panel,
                                    activeforeground=text_fg)
                elif wtype == "Message":
                    child.configure(bg=bg, fg=text_fg)
                elif wtype == "Scrollbar":
                    child.configure(bg=panel_alt, troughcolor=bg,
                                    activebackground=colors.get("red", "#f0541c"))
            except tk.TclError:
                pass

            # Always recurse regardless of widget type
            self._walk(child, colors)

    def create_theme_toggle_button(self, parent, callback=None):
        """Create a theme toggle button.

        Blend into the parent header: parent-matching background is
        Tkinter's equivalent of transparency (Tk widgets have no alpha).
        Shows a SUN while the dark theme is active (click -> light) and a
        MOON while light is active (click -> dark)."""
        import tkinter as tk

        try:
            bg = parent.cget("bg")
        except Exception:
            # ttk parents have no -bg option; use the brand band navy.
            bg = self.BRAND_NAVY

        btn = tk.Label(
            parent,
            text="\u2600" if self.current_theme == "dark" else "\u263e",
            bg=bg,
            fg=self.BRAND_WHITE,
            font=("Segoe UI Symbol", 13),
            cursor="hand2",
            padx=8,
            pady=2,
        )
        btn._tag = "header_label"  # theme walks must never recolor it
        btn.bind("<Button-1>", lambda e: self._on_toggle(btn, callback))
        return btn

    def _on_toggle(self, btn, callback):
        new_theme = self.toggle()
        btn.configure(text="\u2600" if new_theme == "dark" else "\u263e")
        if callback:
            callback(new_theme)

    @staticmethod
    def get_copyright_year():
        return datetime.now().year

    @staticmethod
    def get_copyright_text():
        return f"Developed by www.3SVerse.com | Copyright © {datetime.now().year} | All rights reserved."


def apply_theme_to_window(window, theme_manager=None):
    """Convenience function."""
    if theme_manager is None:
        theme_manager = ThemeManager()
    theme_manager.apply_theme_to_window(window)


def get_copyright_year():
    return ThemeManager.get_copyright_year()


# ── Theme-toggle vector glyph (sun / crescent moon) ─────────────────────────
# Tk renders emoji (☀️/🌙) as flat monochrome outlines, where a small sun is
# easy to mistake for a moon. Drawing the icon as vector art on a canvas gives
# a genuinely transparent background AND an unmistakable glyph: dark theme
# shows a sun (ring + 8 rays — click goes light), light theme shows a real
# crescent (click goes dark).

def draw_theme_glyph(canvas, cx, cy, theme, tags=("theme_toggle",), color="#ffffff"):
    """Paint the theme-toggle glyph for `theme` centered at (cx, cy).

    Items are created with the given `tags`; callers own deleting and
    re-drawing (e.g. on <Configure>) and can tag_bind clicks/cursor on the
    tag — canvas tag bindings also apply to items created later with the
    same tag.
    """
    import math

    if theme == "light":
        # Crescent: outer disc minus an equal-radius disc offset right.
        R = 8.0
        d = 5.5
        half = math.acos(d / (2 * R))
        pts = []
        steps = 36
        sweep = 2 * math.pi - 2 * half
        for i in range(steps + 1):
            a = -half - sweep * i / steps
            pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        a_end = math.atan2(R * math.sin(half), R * math.cos(half) - d)
        a_start = math.atan2(R * math.sin(-half), R * math.cos(-half) - d)
        for i in range(steps + 1):
            a = a_end + (math.pi - a_end) * i / steps
            pts.append((cx + d + R * math.cos(a), cy + R * math.sin(a)))
        for i in range(steps + 1):
            a = -math.pi + (a_start + math.pi) * i / steps
            pts.append((cx + d + R * math.cos(a), cy + R * math.sin(a)))
        canvas.create_polygon(pts, smooth=True, fill=color,
                              outline="", width=0, tags=tags)
    else:
        # Sun: ring + 8 rays.
        r = 6.0
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           outline=color, width=2, tags=tags)
        for i in range(8):
            a = math.radians(i * 45)
            canvas.create_line(
                cx + math.cos(a) * (r + 2.5), cy + math.sin(a) * (r + 2.5),
                cx + math.cos(a) * (r + 6.5), cy + math.sin(a) * (r + 6.5),
                fill=color, width=2, tags=tags)


# ── Standard theme-toggle canvas (vector sun/crescent, right-center) ────────
# One shared builder for ALL 3SVerse apps: a vector sun (dark theme) /
# crescent moon (light theme) drawn on a flat canvas — genuinely transparent
# on the navy header, and an unmistakable glyph (Tk renders emoji as flat
# monochrome outlines where a small sun is easy to mistake for a moon).
# Click runs on_click() (app-specific toggle + apply), then redraws.
def create_toggle_canvas(parent, theme_manager, on_click, size=36, bg="#090d26"):
    import tkinter as tk

    canvas = tk.Canvas(parent, width=size, height=size, bg=bg,
                       highlightthickness=0, bd=0, cursor="hand2")

    def render():
        canvas.delete("theme_toggle")
        draw_theme_glyph(
            canvas, size / 2.0, size / 2.0,
            "dark" if getattr(theme_manager, "current_theme", "light") == "dark" else "light",
            tags=("theme_toggle",),
        )

    def _click(_event=None):
        try:
            if on_click:
                on_click()
        finally:
            render()

    canvas.bind("<Button-1>", _click)
    canvas._render_theme_glyph = render
    canvas._tag = "header"
    render()
    return canvas


# ════════════════════════════════════════════════════════════════════════════
# PRO UI LAYER (3SVerse design system) - one polish pass shared by every app.
#   * flat primary / secondary buttons with real hover + pressed states
#   * 1px hairline inputs with an accent focus ring and comfortable padding
#   * flat table headings, taller rows, accent selection
#   * accent-topped notebook tabs, thin progress bar
#   * slim dark ttk scrollbars (replaces the bulky native ones)
#   * one font family (Segoe UI) with a monospace log font
# Call install_pro_widgets() BEFORE building the UI and polish_ui(root, colors)
# after every theme apply. Everything is wrapped in try/except: styling must
# never be able to break an app.
# ════════════════════════════════════════════════════════════════════════════
_PRO_FONT = "Segoe UI"
_PRO_MONO = "Consolas"
_PRO_PRIMARY_TEXTS = ("start filing", "start automation", "run now", "run all stores",
                      "save all settings", "save all info")


def install_pro_widgets():
    """Swap the bulky native tk.Scrollbar for a themeable slim ttk one."""
    import tkinter as tk
    from tkinter import ttk

    if getattr(tk, "_vp_pro_scrollbar", False):
        return

    class _ProScrollbar(ttk.Scrollbar):
        _DROP = ("bg", "background", "troughcolor", "activebackground", "width",
                 "relief", "bd", "borderwidth", "highlightthickness",
                 "highlightbackground", "highlightcolor", "elementborderwidth",
                 "jump", "activerelief", "repeatdelay", "repeatinterval")

        def __init__(self, master=None, **kw):
            for k in self._DROP:
                kw.pop(k, None)
            ttk.Scrollbar.__init__(self, master, **kw)

        def configure(self, cnf=None, **kw):
            for k in self._DROP:
                kw.pop(k, None)
            if isinstance(cnf, dict):
                cnf = {k: v for k, v in cnf.items() if k not in self._DROP}
            return ttk.Scrollbar.configure(self, cnf, **kw)
        config = configure

    tk.Scrollbar = _ProScrollbar
    try:
        import tkinter.scrolledtext as _st
        _st.Scrollbar = _ProScrollbar
    except Exception:
        pass
    tk._vp_pro_scrollbar = True


def _pro_rgb(widget, color):
    try:
        r, g, b = widget.winfo_rgb(color)
        return r // 257, g // 257, b // 257
    except Exception:
        return 0, 0, 0


def _pro_mix(widget, a, b, t):
    ra, ga, ba = _pro_rgb(widget, a)
    rb, gb, bb = _pro_rgb(widget, b)
    return "#%02x%02x%02x" % (round(ra + (rb - ra) * t), round(ga + (gb - ga) * t),
                              round(ba + (bb - ba) * t))


def _pro_font(font, family=None, min_size=None, weight=None):
    """Normalise a Tk font spec to the app family, keeping size/weight."""
    import tkinter.font as tkfont
    try:
        f = tkfont.Font(font=font)
        size = abs(int(f.actual("size")))
        bold = f.actual("weight") == "bold"
    except Exception:
        size, bold = 10, False
    if min_size and size < min_size:
        size = min_size
    w = weight or ("bold" if bold else "normal")
    return (family or _PRO_FONT, size, w)


def polish_ui(root, colors=None):
    """Apply the 3SVerse pro look to `root` and every child widget."""
    import tkinter as tk
    from tkinter import ttk
    import tkinter.font as tkfont

    try:
        c = dict(colors or {})
        bg = c.get("bg") or root.cget("bg")
        panel = c.get("panel") or bg
        alt = c.get("panel_alt") or panel
        text = c.get("text") or "#e8ecf7"
        dim = c.get("text_dim") or text
        accent = c.get("red") or c.get("accent") or "#f0541c"
        inputbg = c.get("input") or alt
        hair = _pro_mix(root, panel, text, 0.16)
        hair_soft = _pro_mix(root, panel, text, 0.09)
        alt_hover = _pro_mix(root, alt, text, 0.09)
        accent_hover = _pro_mix(root, accent, "#000000", 0.12)
        accent_press = _pro_mix(root, accent, "#000000", 0.24)
        sel_bg = _pro_mix(root, panel, accent, 0.38)
        on_accent = "#ffffff"
    except Exception:
        return

    # ---- named fonts: one family everywhere -------------------------------
    try:
        for name, size in (("TkDefaultFont", 10), ("TkTextFont", 10), ("TkMenuFont", 10),
                           ("TkHeadingFont", 10), ("TkCaptionFont", 10),
                           ("TkSmallCaptionFont", 9), ("TkIconFont", 10),
                           ("TkTooltipFont", 9)):
            tkfont.nametofont(name).configure(family=_PRO_FONT, size=size)
        tkfont.nametofont("TkFixedFont").configure(family=_PRO_MONO, size=10)
    except Exception:
        pass

    # ---- ttk styles --------------------------------------------------------
    try:
        st = ttk.Style(root)
        try:
            st.theme_use("clam")
        except Exception:
            pass
        st.configure("TNotebook", background=bg, borderwidth=0, tabmargins=(0, 6, 0, 0))
        st.configure("TNotebook.Tab", background=bg, foreground=dim, padding=(20, 8),
                     borderwidth=0, font=(_PRO_FONT, 10, "bold"),
                     lightcolor=bg, darkcolor=bg, bordercolor=bg)
        st.map("TNotebook.Tab",
               background=[("selected", panel), ("active", alt)],
               foreground=[("selected", text), ("active", text)],
               lightcolor=[("selected", accent), ("active", alt)],
               darkcolor=[("selected", panel), ("active", alt)],
               bordercolor=[("selected", panel), ("active", alt)],
               expand=[("selected", (0, 0, 0, 0))])
        st.configure("Treeview", background=panel, fieldbackground=panel, foreground=text,
                     rowheight=28, borderwidth=0, bordercolor=hair, lightcolor=panel,
                     darkcolor=panel, font=(_PRO_FONT, 10))
        st.map("Treeview", background=[("selected", sel_bg)],
               foreground=[("selected", text)])
        # Panel / table headers stay DARK NAVY with white text in BOTH themes and
        # never change on hover or press (no "hover walk").
        navy = c.get("navy") or "#090d26"
        st.configure("Treeview.Heading", background=navy, foreground="#ffffff", relief="flat",
                     borderwidth=0, padding=(12, 9), font=(_PRO_FONT, 9, "bold"),
                     lightcolor=navy, darkcolor=navy, bordercolor=navy)
        st.map("Treeview.Heading",
               background=[("active", navy), ("pressed", navy), ("!active", navy)],
               foreground=[("active", "#ffffff"), ("pressed", "#ffffff"), ("!active", "#ffffff")],
               lightcolor=[("active", navy), ("pressed", navy), ("!active", navy)],
               darkcolor=[("active", navy), ("pressed", navy), ("!active", navy)],
               bordercolor=[("active", navy), ("pressed", navy), ("!active", navy)])
        st.configure("Horizontal.TProgressbar", thickness=8, troughcolor=alt,
                     background=accent, lightcolor=accent, darkcolor=accent,
                     bordercolor=alt, borderwidth=0)
        st.configure("TCombobox", fieldbackground=inputbg, background=alt, foreground=text,
                     arrowcolor=dim, bordercolor=hair, lightcolor=hair, darkcolor=hair,
                     padding=5, arrowsize=14)
        st.map("TCombobox", bordercolor=[("focus", accent)], lightcolor=[("focus", accent)],
               darkcolor=[("focus", accent)],
               fieldbackground=[("readonly", inputbg)], foreground=[("readonly", text)])
        st.configure("TEntry", fieldbackground=inputbg, foreground=text, bordercolor=hair,
                     lightcolor=hair, darkcolor=hair, padding=5)
        st.map("TEntry", bordercolor=[("focus", accent)], lightcolor=[("focus", accent)],
               darkcolor=[("focus", accent)])

        st.configure("TButton", background=_pro_mix(root, panel, text, 0.10), foreground=text,
                     bordercolor=hair, lightcolor=_pro_mix(root, panel, text, 0.10),
                     darkcolor=_pro_mix(root, panel, text, 0.10), focuscolor=panel,
                     padding=(14, 6), relief="flat", borderwidth=1, font=(_PRO_FONT, 10, "bold"))
        st.map("TButton",
               background=[("disabled", _pro_mix(root, panel, text, 0.05)),
                           ("pressed", _pro_mix(root, panel, text, 0.24)),
                           ("active", _pro_mix(root, panel, text, 0.17))],
               foreground=[("disabled", dim)],
               bordercolor=[("active", accent), ("pressed", accent)],
               lightcolor=[("active", _pro_mix(root, panel, text, 0.17)),
                           ("pressed", _pro_mix(root, panel, text, 0.24))],
               darkcolor=[("active", _pro_mix(root, panel, text, 0.17)),
                          ("pressed", _pro_mix(root, panel, text, 0.24))])
        st.configure("Accent.TButton", background=accent, foreground=on_accent,
                     bordercolor=accent, lightcolor=accent, darkcolor=accent,
                     focuscolor=accent, padding=(16, 6), relief="flat", borderwidth=1,
                     font=(_PRO_FONT, 10, "bold"))
        st.map("Accent.TButton",
               background=[("disabled", _pro_mix(root, panel, accent, 0.35)),
                           ("pressed", accent_press), ("active", accent_hover)],
               foreground=[("disabled", _pro_mix(root, panel, on_accent, 0.55))],
               bordercolor=[("disabled", _pro_mix(root, panel, accent, 0.35)),
                            ("pressed", accent_press), ("active", accent_hover)],
               lightcolor=[("pressed", accent_press), ("active", accent_hover)],
               darkcolor=[("pressed", accent_press), ("active", accent_hover)])
        st.configure("TLabelframe", background=panel, bordercolor=hair, lightcolor=hair,
                     darkcolor=hair, relief="solid", borderwidth=1)
        st.configure("TLabelframe.Label", background=panel, foreground=text,
                     font=(_PRO_FONT, 10, "bold"))
        st.configure("TSeparator", background=hair)
        # draggable split-view handles: visible dotted grip, accent on hover
        sash_bg = _pro_mix(root, bg, text, 0.10)
        st.configure("TPanedwindow", background=bg)
        st.configure("Sash", sashthickness=9, gripcount=7, handlesize=9, background=sash_bg,
                     lightcolor=_pro_mix(root, bg, text, 0.30), darkcolor=_pro_mix(root, bg, text, 0.30),
                     bordercolor=bg, sashpad=0)
        st.map("Sash", background=[("active", accent)], lightcolor=[("active", on_accent)],
               darkcolor=[("active", on_accent)])
        thumb = _pro_mix(root, panel, text, 0.26)
        thumb_hot = _pro_mix(root, panel, text, 0.42)
        for orient, trough in (("Vertical", "ns"), ("Horizontal", "ew")):
            name = f"{orient}.TScrollbar"
            st.layout(name, [(f"{orient}.Scrollbar.trough", {"sticky": trough, "children": [
                (f"{orient}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
            st.configure(name, troughcolor=bg, background=thumb, bordercolor=bg,
                         lightcolor=thumb, darkcolor=thumb, gripcount=0, borderwidth=0,
                         width=10, arrowsize=10)
            st.map(name, background=[("active", thumb_hot), ("pressed", thumb_hot)],
                   lightcolor=[("active", thumb_hot), ("pressed", thumb_hot)],
                   darkcolor=[("active", thumb_hot), ("pressed", thumb_hot)])
    except Exception:
        pass

    # ---- classic tk widgets -----------------------------------------------
    def _gm_pad(w, ipady):
        try:
            if getattr(w, "_vp_ipad", False):
                return
            mgr = w.winfo_manager()
            if mgr == "pack":
                w.pack_configure(ipady=ipady)
            elif mgr == "grid":
                w.grid_configure(ipady=ipady)
            w._vp_ipad = True
        except Exception:
            pass

    def _btn(w):
        try:
            cur_bg = w.cget("bg")
            primary = getattr(w, "_vp_primary", None)
            if primary is None:
                _t = str(w.cget("text")).strip().lower()
                if (getattr(w, "_tag", None) in ("save", "primary")
                        or _t in _PRO_PRIMARY_TEXTS):
                    primary = True
                    w._vp_primary = True
            if primary is None:
                primary = False        # only Start/Run/Save actions are accent
                w._vp_primary = False
            parent_bg = panel
            try:
                parent_bg = w.master.cget("bg")
            except Exception:
                pass
            if primary:
                base, hover, press, fg = accent, accent_hover, accent_press, on_accent
                w.configure(highlightthickness=0, bd=0)
            else:
                base = _pro_mix(w, parent_bg, text, 0.10)
                hover = _pro_mix(w, parent_bg, text, 0.17)
                press = _pro_mix(w, parent_bg, text, 0.24)
                fg = text
                w.configure(highlightthickness=1, bd=0, highlightbackground=hair,
                            highlightcolor=accent)
            w._vp_colors = (base, hover, press)
            w.configure(bg=base, fg=fg, activebackground=press, activeforeground=fg,
                        relief="flat", cursor="hand2", disabledforeground=_pro_mix(w, base, text, 0.40),
                        font=_pro_font(w.cget("font"), min_size=10, weight="bold"),
                        padx=16, pady=6)
            if not getattr(w, "_vp_bound", False):
                def _enter(_e=None, _w=w):
                    try:
                        if str(_w.cget("state")) != "disabled":
                            _w.configure(bg=_w._vp_colors[1])
                    except Exception:
                        pass

                def _leave(_e=None, _w=w):
                    try:
                        _w.configure(bg=_w._vp_colors[0])
                    except Exception:
                        pass
                w.bind("<Enter>", _enter, add="+")
                w.bind("<Leave>", _leave, add="+")
                w._vp_bound = True
        except Exception:
            pass

    def _entry(w):
        try:
            w.configure(relief="flat", bd=0, highlightthickness=1, highlightbackground=hair,
                        highlightcolor=accent, insertbackground=text, bg=inputbg, fg=text,
                        selectbackground=accent, selectforeground=on_accent,
                        font=_pro_font(w.cget("font"), min_size=10))
            try:
                w.configure(disabledbackground=alt, readonlybackground=alt,
                            disabledforeground=dim)
            except Exception:
                pass
            _gm_pad(w, 3)
        except Exception:
            pass

    def _text(w):
        try:
            fam = None
            try:
                fam = tkfont.Font(font=w.cget("font")).actual("family")
            except Exception:
                pass
            mono = bool(fam) and any(k in fam.lower() for k in ("consol", "courier", "mono", "cascadia"))
            w.configure(relief="flat", bd=0, highlightthickness=1, highlightbackground=hair,
                        highlightcolor=accent, insertbackground=text, padx=10, pady=8,
                        selectbackground=accent, selectforeground=on_accent,
                        font=_pro_font(w.cget("font"), family=_PRO_MONO if mono else _PRO_FONT, min_size=10))
        except Exception:
            pass

    def _walk(w):
        try:
            cls = w.winfo_class()
        except Exception:
            return
        tag = getattr(w, "_tag", None)
        header_zone = tag in ("header", "header_label", "brand", "logo", "footer")
        if not header_zone:
            if cls == "Button":
                _btn(w)
            elif cls == "TButton":
                try:
                    _t = str(w.cget("text")).strip().lower()
                    if _t in _PRO_PRIMARY_TEXTS:
                        w.configure(style="Accent.TButton")
                    w.configure(cursor="hand2")
                except Exception:
                    pass
            elif cls == "Entry":
                _entry(w)
            elif cls == "Text":
                _text(w)
            elif cls == "Labelframe":
                try:
                    w.configure(bd=0, relief="flat", highlightthickness=1,
                                highlightbackground=hair, highlightcolor=hair,
                                fg=text, font=_pro_font(w.cget("font"), min_size=10, weight="bold"),
                                padx=10, pady=6)
                except Exception:
                    pass
            elif cls in ("Radiobutton", "Checkbutton"):
                try:
                    w.configure(cursor="hand2", activebackground=w.cget("bg"),
                                activeforeground=text, selectcolor=inputbg,
                                font=_pro_font(w.cget("font")))
                except Exception:
                    pass
            elif cls == "Label":
                try:
                    w.configure(font=_pro_font(w.cget("font")))
                except Exception:
                    pass
        for ch in w.winfo_children():
            _walk(ch)

    try:
        _walk(root)
    except Exception:
        pass


# ── Resizable panels, scroll-when-needed, wrapping toolbars ────────────────
def make_resizable(parent, panes, orient="horizontal", weights=None, minsizes=None,
                   ratios=None, last_size=None):
    """Turn already laid-out SIBLING panes into a split view with a draggable
    sash between them. Panes keep their current size; extra space follows
    `weights`; `minsizes` stop a pane being dragged shut."""
    from tkinter import ttk
    try:
        n = len(panes)
        weights = weights or [1] * n
        minsizes = minsizes or [60] * n
        horiz = orient == "horizontal"
        sizes = [(p.winfo_width() if horiz else p.winfo_height()) or
                 (p.winfo_reqwidth() if horiz else p.winfo_reqheight()) for p in panes]
        mgr = panes[0].winfo_manager()
        pw = ttk.PanedWindow(parent, orient=orient)
        if mgr == "grid":
            infos = [p.grid_info() for p in panes]
            r0 = min(int(i["row"]) for i in infos)
            c0 = min(int(i["column"]) for i in infos)
            r1 = max(int(i["row"]) + int(i.get("rowspan", 1)) for i in infos)
            c1 = max(int(i["column"]) + int(i.get("columnspan", 1)) for i in infos)
            pw.grid(row=r0, column=c0, rowspan=r1 - r0, columnspan=c1 - c0, sticky="nsew")
            parent.grid_columnconfigure(c0, weight=1)
            parent.grid_rowconfigure(r0, weight=1)
            for p in panes:
                p.grid_forget()
        elif mgr == "pack":
            info = panes[0].pack_info()
            pw.pack(before=panes[0], fill="both", expand=True,
                    side=info.get("side", "top"))
            for p in panes:
                p.pack_forget()
        else:
            return None
        for p, w in zip(panes, weights):
            pw.add(p, weight=w)
            try:
                p.lift(pw)       # panes were created BEFORE pw: raise them above it
            except Exception:
                p.lift()

        def _apply_initial():
            try:
                pw.update_idletasks()
                total = pw.winfo_width() if horiz else pw.winfo_height()
                if total <= 1:
                    pw.after(60, _apply_initial)
                    return
                pos = 0
                for i in range(n - 1):
                    if ratios:
                        pos = int(total * sum(ratios[:i + 1]) / float(sum(ratios)))
                    elif last_size and i == n - 2:
                        pos = total - last_size
                    else:
                        pos += sizes[i]
                    lo = sum(minsizes[:i + 1])
                    hi = total - sum(minsizes[i + 1:])
                    pw.sashpos(i, max(lo, min(pos, hi)))
            except Exception:
                pass
        pw.after(80, _apply_initial)
        _st = {"drag": False, "t0": None}

        def _settle(_e=None):
            # window is still being maximised/shown: keep the INITIAL proportions until
            # the user touches a sash (or ~2s have passed)
            try:
                import time as _t
                if _st["t0"] is None:
                    _st["t0"] = _t.time()
                if not _st["drag"] and _t.time() - _st["t0"] < 2.0:
                    pw.after_idle(_apply_initial)
            except Exception:
                pass
        pw.bind("<Configure>", _settle, add="+")
        pw.bind("<ButtonPress-1>", lambda _e: _st.__setitem__("drag", True), add="+")

        def _clamp(_e=None):
            try:
                total = pw.winfo_width() if horiz else pw.winfo_height()
                for i in range(n - 1):
                    lo = sum(minsizes[:i + 1])
                    hi = total - sum(minsizes[i + 1:])
                    cur = pw.sashpos(i)
                    if cur < lo:
                        pw.sashpos(i, lo)
                    elif cur > hi > lo:
                        pw.sashpos(i, hi)
            except Exception:
                pass
        pw.bind("<B1-Motion>", _clamp, add="+")
        pw.bind("<ButtonRelease-1>", _clamp, add="+")
        pw.configure(cursor="sb_h_double_arrow" if horiz else "sb_v_double_arrow")
        return pw
    except Exception:
        return None


def make_scrollable(root, body, min_w=0, min_h=0):
    """Wrap `body` so scrollbars appear ONLY when the window is smaller than the
    content needs (vertical and/or horizontal). Mouse wheel scrolls it."""
    import tkinter as tk
    from tkinter import ttk
    try:
        mgr = body.winfo_manager()
        if mgr not in ("pack", "grid") or getattr(body, "_vp_scroll", False):
            return None
        info = body.grid_info() if mgr == "grid" else body.pack_info()
        info.pop("in", None)
        try:
            bgc = ttk.Style(root).lookup("TFrame", "background") or root.cget("bg")
        except Exception:
            bgc = "#000000"
        try:
            bgc = body.cget("bg")
        except Exception:
            pass
        holder = tk.Frame(root, bd=0, highlightthickness=0, bg=bgc)
        holder.grid_rowconfigure(0, weight=1)
        holder.grid_columnconfigure(0, weight=1)
        cv = tk.Canvas(holder, highlightthickness=0, bd=0, bg=bgc)
        # Scrollbars are children of ROOT (not holder) and are placed over the
        # holder's right/bottom edge: `body` is a sibling of the canvas, so it is
        # stacked above holder and its own children - the bars must be above it.
        vs = ttk.Scrollbar(root, orient="vertical", command=cv.yview)
        hs = ttk.Scrollbar(root, orient="horizontal", command=cv.xview)
        cv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        cv.grid(row=0, column=0, sticky="nsew")
        # order matters: put the holder in body's slot FIRST (body is still managed
        # by pack/grid), release body, and only then hand it to the canvas.
        if mgr == "grid":
            holder.grid(**info)
            body.grid_forget()
        else:
            holder.pack(after=body, **info)
            body.pack_forget()
        win = cv.create_window(0, 0, anchor="nw", window=body)
        body._vp_scroll = True
        body.lift()   # window items must sit ABOVE the canvas holder in stacking order
        state = {"v": False, "h": False, "last": None}
        BAR = 12

        def _restack():
            # header / footer / other siblings and the bars must sit ABOVE body so
            # the overflowing part of body is hidden behind them (body is not clipped)
            try:
                for w in root.winfo_children():
                    # never touch Menus / Toplevels: raising an (unposted) popup menu
                    # makes it appear at the top-left corner of the screen
                    if w is body or w is holder:
                        continue
                    if w.winfo_class() in ("Menu", "Toplevel") or w.winfo_toplevel() is w:
                        continue
                    w.lift()
                if state["v"]:
                    vs.lift()
                if state["h"]:
                    hs.lift()
            except Exception:
                pass

        def sync(_e=None):
            try:
                cw, ch = holder.winfo_width(), holder.winfo_height()
                if cw <= 1 or ch <= 1:
                    return
                rw = min_w or body.winfo_reqwidth()
                rh = min_h or body.winfo_reqheight()
                need_v, need_h = ch < rh, cw < rw
                if need_v and not need_h and cw - BAR < rw:
                    need_h = True
                if need_h and not need_v and ch - BAR < rh:
                    need_v = True
                aw = cw - (BAR if need_v else 0)
                ah = ch - (BAR if need_h else 0)
                bw, bh = max(aw, rw), max(ah, rh)
                key = (bw, bh, need_v, need_h)
                if key == state["last"]:
                    return
                state["last"] = key
                cv.itemconfigure(win, width=bw, height=bh)
                cv.configure(scrollregion=(0, 0, bw, bh))
                if need_v != state["v"]:
                    if need_v:
                        vs.place(in_=holder, relx=1.0, x=-BAR, y=0, width=BAR,
                                 relheight=1.0, height=-(BAR if need_h else 0))
                    else:
                        vs.place_forget()
                    state["v"] = need_v
                if need_h != state["h"]:
                    if need_h:
                        hs.place(in_=holder, rely=1.0, y=-BAR, x=0, height=BAR,
                                 relwidth=1.0, width=-(BAR if need_v else 0))
                    else:
                        hs.place_forget()
                    state["h"] = need_h
                _restack()
                if not need_v:
                    cv.yview_moveto(0)
                if not need_h:
                    cv.xview_moveto(0)
            except Exception:
                pass

        holder.bind("<Configure>", sync)
        body.bind("<Configure>", lambda e: holder.after_idle(sync), add="+")

        def _wheel(e):
            try:
                if not (state["v"] or state["h"]):
                    return
                w = holder.winfo_containing(e.x_root, e.y_root)
                if w is None:
                    return
                p = w
                while p is not None and p is not holder:
                    if p.winfo_class() in ("Text", "Treeview", "Listbox", "TCombobox",
                                           "Scrolledtext"):
                        return
                    p = p.master
                if p is None:
                    return
                if e.state & 0x1 and state["h"]:
                    cv.xview_scroll(-1 if e.delta > 0 else 1, "units")
                elif state["v"]:
                    cv.yview_scroll(-1 if e.delta > 0 else 1, "units")
            except Exception:
                pass
        holder.bind_all("<MouseWheel>", _wheel, add="+")
        holder.after(120, lambda: (sync(), _restack()))
        return holder
    except Exception:
        return None


def make_flow(frame, hpad=6, vpad=4):
    """Make a row of buttons WRAP onto extra lines instead of being cut off at
    the right edge of a narrow window."""
    try:
        kids = [c for c in frame.winfo_children() if c.winfo_manager() in ("pack", "grid")]
        if len(kids) < 2 or getattr(frame, "_vp_flow", False):
            return
        for c in kids:
            if c.winfo_manager() == "pack":
                c.pack_forget()
            else:
                c.grid_forget()
        frame._vp_flow = True
        last = {"w": -1}

        def layout(_e=None):
            try:
                w = frame.winfo_width()
                if w <= 1 or w == last["w"]:
                    return
                last["w"] = w
                x = row = col = 0
                for c in kids:
                    cw = c.winfo_reqwidth() + hpad
                    if x + cw > w and col > 0:
                        row += 1
                        col = 0
                        x = 0
                    c.grid(row=row, column=col, padx=(0, hpad), pady=(0, vpad), sticky="w")
                    col += 1
                    x += cw
            except Exception:
                pass
        frame.bind("<Configure>", layout, add="+")
        frame.after(60, layout)
    except Exception:
        pass


def make_standard_footer(parent, deactivate_cb=None, side="bottom", grid_kw=None,
                         extra="  |  Independent vendor - not affiliated with VidaPay."):
    """THE footer for every VidaPay app: 24px navy bar, copyright text centred
    across the full width, and (when a callback is given) the 'Deactivate this
    PC' link pinned to the RIGHT edge, vertically centred. Built with place()
    so alignment never depends on text lengths or window width."""
    import tkinter as tk
    from datetime import date
    navy, dim = "#090d26", "#9d9db8"
    bar = tk.Frame(parent, bg=navy, height=24)
    if grid_kw is not None:
        bar.grid(**grid_kw)
        bar.grid_propagate(False)
    else:
        bar.pack(fill="x", side=side)
        bar.pack_propagate(False)
    bar._tag = "footer"
    lbl = tk.Label(bar, text=f"Developed by www.3SVerse.com | Copyright \u00a9 {date.today().year} | All rights reserved.{extra}",
                   font=("Segoe UI", 8), fg=dim, bg=navy, bd=0, highlightthickness=0)
    lbl.place(relx=0.5, rely=0.5, anchor="center")
    lbl._tag = "footer_label"
    _full = lbl.cget("text")
    _short = f"Developed by www.3SVerse.com | Copyright \u00a9 {date.today().year}"

    def _fit(_e=None):
        # keep the centred text clear of the right-hand link on narrow windows
        try:
            w = bar.winfo_width()
            lbl.configure(text=_full if w >= 1000 else (_short if w >= 560 else ""))
        except Exception:
            pass
    bar.bind("<Configure>", _fit, add="+")
    if deactivate_cb is not None:
        link = tk.Label(bar, text="Deactivate this PC", font=("Segoe UI", 8, "underline"),
                        fg=dim, bg=navy, cursor="hand2", bd=0, highlightthickness=0)
        link.place(relx=1.0, rely=0.5, anchor="e", x=-14)
        link.bind("<Button-1>", lambda _e: deactivate_cb())
        link._tag = "footer_label"
    return bar
