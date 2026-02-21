import os
import sys
import subprocess

# Imports
# ---------------------------------------------------------------------------

import gi
gi.require_version("Gtk",    "4.0")
gi.require_version("Adw",    "1")
gi.require_version("WebKit", "6.0")

from gi.repository import Gtk, Adw, WebKit, Gio, Gdk, Pango

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OFFICE_APPS = [
    ("Office",     "https://www.office.com"),
    ("Word",       "https://www.office.com/launch/word"),
    ("Excel",      "https://www.office.com/launch/excel"),
    ("PowerPoint", "https://www.office.com/launch/powerpoint"),
    ("OneNote",    "https://www.office.com/launch/onenote"),
    ("Outlook",    "https://outlook.office.com"),
]

APP_URL_PATTERNS = {
    "Office":     ["office.com"],
    "Word":       ["word", "/launch/word"],
    "Excel":      ["excel", "/launch/excel"],
    "PowerPoint": ["powerpoint", "/launch/powerpoint"],
    "OneNote":    ["onenote", "/launch/onenote"],
    "Outlook":    ["outlook.office.com", "outlook.live.com"],
}

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

APP_CSS = """
/* ── App switcher buttons (Office / Word / Excel …) ── */

/* Foreground: this app's tab is currently selected */
button.app-active {
    background-color: @accent_bg_color;
    color: @accent_fg_color;
    border-radius: 6px;
    box-shadow: none;
}
button.app-active:hover {
    background-color: mix(@accent_bg_color, white, 0.12);
}

/* Open but in background — tinted with underline indicator */
button.app-open {
    background-color: alpha(@accent_bg_color, 0.18);
    color: @accent_fg_color;
    border-radius: 6px;
    box-shadow: inset 0 -2px 0 0 @accent_bg_color;
}
button.app-open:hover {
    background-color: alpha(@accent_bg_color, 0.30);
}

/* Not open */
button.app-inactive {
    background: none;
    box-shadow: none;
    color: @headerbar_fg_color;
}
button.app-inactive:hover {
    background-color: alpha(@headerbar_fg_color, 0.10);
    border-radius: 6px;
}

/* ── Header bar "Close Word / Close Excel" button ── */
button.close-tab-btn {
    background-color: alpha(@headerbar_fg_color, 0.12);
    color: @headerbar_fg_color;
    border-radius: 6px;
    padding: 4px 12px;
    box-shadow: none;
}
button.close-tab-btn:hover {
    background-color: alpha(@error_color, 0.18);
    color: @error_color;
}
button.close-tab-btn:active {
    background-color: alpha(@error_color, 0.30);
    color: @error_color;
}

/* ── Custom tab strip ── */
.tab-strip {
    background-color: @headerbar_bg_color;
    border-bottom: 1px solid @borders;
    padding: 4px 6px;
}

/* Inactive tab button */
button.tab-btn {
    background-color: alpha(@window_fg_color, 0.08);
    color: @window_fg_color;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.85em;
    min-width: 80px;
    min-height: 28px;
    box-shadow: none;
}

/* Active tab button */
button.tab-btn-active {
    background-color: @accent_bg_color;
    color: @accent_fg_color;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.85em;
    min-width: 80px;
    min-height: 28px;
    box-shadow: none;
}

/* Close button inside each tab */
button.tab-close {
    background: none;
    box-shadow: none;
    border-radius: 4px;
    padding: 0px 2px;
    min-width: 0;
    min-height: 0;
}
button.tab-close:hover {
    background-color: alpha(@window_fg_color, 0.15);
}
""".encode()


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class OfficeApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.mrks.office-gtk4",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        if not hasattr(self, "win") or self.win is None:
            self.win = OfficeWindow(application=self)
        self.win.present()


# ---------------------------------------------------------------------------
# Tab data class
# ---------------------------------------------------------------------------

class TabEntry:
    """Holds everything associated with one open tab."""
    def __init__(self, page, wv, btn, label_widget, track_label=None):
        self.page         = page          # AdwTabPage
        self.wv           = wv            # WebKit.WebView
        self.btn          = btn           # Gtk.Button in the custom tab strip
        self.label_widget = label_widget  # Gtk.Label inside the button
        self.track_label  = track_label   # e.g. "Word", or None for generic tabs


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class OfficeWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(1280, 900)
        self.set_title("Microsoft Office Online")

        # label -> TabEntry  (named app tabs only)
        self._named_tabs: dict   = {}
        # AdwTabPage -> TabEntry  (all tabs)
        self._all_tabs: dict     = {}
        # App switcher buttons
        self._app_buttons: dict  = {}
        self._root_wv            = None

        self._load_css()
        self._setup_session()
        self._build_ui()

        self._open_tab("https://www.office.com", "Office", track_label="Office")

    # -----------------------------------------------------------------------
    # CSS
    # -----------------------------------------------------------------------

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(APP_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    # -----------------------------------------------------------------------
    # Session
    # -----------------------------------------------------------------------

    def _setup_session(self):
        data_path  = os.path.expanduser("~/.local/share/Office-GTK4")
        cache_path = os.path.expanduser("~/.cache/Office-GTK4")
        os.makedirs(data_path,  exist_ok=True)
        os.makedirs(cache_path, exist_ok=True)

        self.session = WebKit.NetworkSession.new(data_path, cache_path)
        cm = self.session.get_cookie_manager()
        cm.set_persistent_storage(
            os.path.join(data_path, "cookies.sqlite"),
            WebKit.CookiePersistentStorage.SQLITE,
        )

    # -----------------------------------------------------------------------
    # UI
    # -----------------------------------------------------------------------

    def _build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer.set_hexpand(True)
        outer.set_vexpand(True)
        self.set_content(outer)

        # ── Header bar ────────────────────────────────────────────────────
        header = Adw.HeaderBar()
        outer.append(header)

        nav_group = Gtk.Box(spacing=0)
        nav_group.add_css_class("linked")
        self._add_nav_btn(nav_group, "go-previous-symbolic",
                          lambda: self._current_wv().go_back(), "Back")
        self._add_nav_btn(nav_group, "go-next-symbolic",
                          lambda: self._current_wv().go_forward(), "Forward")
        self._add_nav_btn(nav_group, "view-refresh-symbolic",
                          lambda: self._current_wv().reload(), "Reload")
        header.pack_start(nav_group)

        # App switcher
        app_switcher = Gtk.Box(spacing=2)
        for label, url in OFFICE_APPS:
            btn = Gtk.Button(label=label)
            btn.add_css_class("flat")
            btn.add_css_class("app-inactive")
            btn.connect("clicked", lambda _, u=url, l=label: self._switch_or_open(l, u))
            app_switcher.append(btn)
            self._app_buttons[label] = btn
        header.set_title_widget(app_switcher)

        self.close_tab_btn = Gtk.Button(label="Close")
        self.close_tab_btn.add_css_class("close-tab-btn")
        self.close_tab_btn.set_visible(False)   # shown only when a closable tab is active
        self.close_tab_btn.connect("clicked", self._on_close_tab_btn_clicked)
        header.pack_end(self.close_tab_btn)

        self.spinner = Gtk.Spinner()
        header.pack_end(self.spinner)

        # ── Custom tab strip (replaces AdwTabBar) ─────────────────────────
        # A horizontal box of styled buttons — one per open tab.
        # Visible only when 2+ tabs are open.
        self.tab_strip = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.tab_strip.add_css_class("tab-strip")
        self.tab_strip.set_visible(False)   # disabled: header bar buttons act as tabs
        # Do NOT append to outer — tab strip is fully disabled

        # ── AdwTabView (manages content, no built-in bar) ─────────────────
        self.tab_view = Adw.TabView()
        self.tab_view.set_hexpand(True)
        self.tab_view.set_vexpand(True)
        outer.append(self.tab_view)

        self.tab_view.connect("notify::selected-page", self._on_selected_page_changed)
        self.tab_view.connect("close-page",            self._on_close_page)
        self.tab_view.connect("create-window",         self._on_create_window)

        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_ctrl)

    # -----------------------------------------------------------------------
    # Custom tab strip management
    # -----------------------------------------------------------------------

    def _make_tab_button(self, title: str, entry_ref: list) -> Gtk.Button:
        """
        Build one tab button: [label ···· close-x]
        entry_ref is a one-element list so the callback can reach the
        TabEntry after it's created (avoids circular dependency).
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        lbl = Gtk.Label(label=title)
        lbl.set_ellipsize(Pango.EllipsizeMode.END)
        lbl.set_max_width_chars(18)
        lbl.set_xalign(0)
        box.append(lbl)

        close_img = Gtk.Image.new_from_icon_name("window-close-symbolic")
        close_btn = Gtk.Button()
        close_btn.set_child(close_img)
        close_btn.add_css_class("tab-close")
        close_btn.set_tooltip_text("Close tab")
        close_btn.connect("clicked", lambda _: self._close_tab_entry(entry_ref[0]))
        box.append(close_btn)

        btn = Gtk.Button()
        btn.set_child(box)
        btn.add_css_class("tab-btn")
        btn.connect("clicked", lambda _: self._select_tab_entry(entry_ref[0]))

        return btn, lbl

    def _add_tab_button(self, entry: TabEntry):
        """Insert a new button into the strip and show the strip if needed."""
        self.tab_strip.append(entry.btn)
        self._update_strip_visibility()

    def _remove_tab_button(self, entry: TabEntry):
        """Remove a tab button from the strip."""
        self.tab_strip.remove(entry.btn)
        self._update_strip_visibility()

    def _update_strip_visibility(self):
        """Tab strip is disabled; header bar buttons serve as tabs."""
        pass  # strip never shown

    def _refresh_tab_buttons(self):
        """Update active/inactive styling on all tab buttons and header app buttons."""
        active_page = self.tab_view.get_selected_page()
        active_entry = self._all_tabs.get(active_page)
        for page, entry in self._all_tabs.items():
            is_active = (page is active_page)
            if is_active:
                entry.btn.remove_css_class("tab-btn")
                entry.btn.add_css_class("tab-btn-active")
            else:
                entry.btn.remove_css_class("tab-btn-active")
                entry.btn.add_css_class("tab-btn")

        # Sync header bar app switcher buttons to reflect open/active/inactive state
        active_label = active_entry.track_label if active_entry else None
        open_labels  = {e.track_label for e in self._all_tabs.values() if e.track_label}
        for label, btn in self._app_buttons.items():
            btn.remove_css_class("app-active")
            btn.remove_css_class("app-open")
            btn.remove_css_class("app-inactive")
            if label == active_label:
                btn.add_css_class("app-active")       # foreground tab
            elif label in open_labels:
                btn.add_css_class("app-open")          # open but in background
            else:
                btn.add_css_class("app-inactive")      # not open at all

        # Show close button only when a named app tab (Word, Excel, …) is active
        # and it isn't the sole remaining tab (so the window stays open).
        is_closable = (
            active_entry is not None
            and active_entry.track_label is not None
            and len(self._all_tabs) > 1
        )
        self.close_tab_btn.set_visible(is_closable)
        if is_closable:
            self.close_tab_btn.set_label(f"Close {active_entry.track_label}")

    def _on_close_tab_btn_clicked(self, _btn):
        page = self.tab_view.get_selected_page()
        if page:
            self.tab_view.close_page(page)

    def _select_tab_entry(self, entry: TabEntry):
        self.tab_view.set_selected_page(entry.page)

    def _close_tab_entry(self, entry: TabEntry):
        self.tab_view.close_page(entry.page)

    # -----------------------------------------------------------------------
    # App button highlighting
    # -----------------------------------------------------------------------

    def _highlight_active_app(self, url: str):
        if not url:
            return
        matched = None
        for label, patterns in APP_URL_PATTERNS.items():
            if any(p in url for p in patterns):
                matched = label
                break
        open_labels = {e.track_label for e in self._all_tabs.values() if e.track_label}
        for label, btn in self._app_buttons.items():
            btn.remove_css_class("app-active")
            btn.remove_css_class("app-open")
            btn.remove_css_class("app-inactive")
            if label == matched:
                btn.add_css_class("app-active")
            elif label in open_labels:
                btn.add_css_class("app-open")
            else:
                btn.add_css_class("app-inactive")

    # -----------------------------------------------------------------------
    # WebView factory
    # -----------------------------------------------------------------------

    def _make_webview(self, related_wv=None) -> WebKit.WebView:
        anchor = related_wv if related_wv is not None else self._root_wv
        kwargs = {}
        if anchor is not None:
            kwargs["related_view"] = anchor
        else:
            kwargs["network_session"] = self.session

        wv = WebKit.WebView(**kwargs)
        wv.set_hexpand(True)
        wv.set_vexpand(True)

        s = wv.get_settings()
        s.set_user_agent(USER_AGENT)
        s.set_enable_javascript(True)
        s.set_enable_javascript_markup(True)
        s.set_enable_media(True)
        s.set_enable_webgl(True)
        s.set_enable_webaudio(True)
        s.set_allow_top_navigation_to_data_urls(False)
        s.set_media_playback_requires_user_gesture(True)
        s.set_hardware_acceleration_policy(WebKit.HardwareAccelerationPolicy.ALWAYS)

        white = Gdk.RGBA()
        white.parse("white")
        wv.set_background_color(white)

        return wv

    # -----------------------------------------------------------------------
    # Tab management
    # -----------------------------------------------------------------------

    def _switch_or_open(self, label: str, url: str):
        entry = self._named_tabs.get(label)
        if entry is not None:
            try:
                self.tab_view.set_selected_page(entry.page)
                return
            except Exception:
                del self._named_tabs[label]
        self._open_tab(url, label, track_label=label)

    def _open_tab(self, url: str, title: str,
                  track_label: str = None,
                  related_wv=None,
                  track: bool = True):
        wv = self._make_webview(related_wv)

        if self._root_wv is None:
            self._root_wv = wv

        page = self.tab_view.append(wv)
        page.set_title(title)

        # Build the tab button with a forward reference so the close/click
        # callbacks can find their TabEntry after construction.
        entry_ref = [None]
        btn, lbl  = self._make_tab_button(title, entry_ref)
        entry     = TabEntry(page, wv, btn, lbl, track_label)
        entry_ref[0] = entry

        self._all_tabs[page] = entry
        if track and track_label:
            self._named_tabs[track_label] = entry

        self._add_tab_button(entry)

        wv.connect("notify::is-loading", self._on_loading_changed)
        wv.connect("notify::title",      self._on_title_changed, entry)
        wv.connect("notify::uri",        self._on_uri_changed)
        wv.connect("create",             self._on_wv_create)

        wv.load_uri(url)
        self.tab_view.set_selected_page(page)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _add_nav_btn(self, container, icon, callback, tooltip=""):
        btn = Gtk.Button(icon_name=icon)
        btn.set_tooltip_text(tooltip)
        btn.connect("clicked", lambda _: callback())
        container.append(btn)

    def _current_wv(self):
        page = self.tab_view.get_selected_page()
        return page.get_child() if page else None

    # -----------------------------------------------------------------------
    # Signal handlers
    # -----------------------------------------------------------------------

    def _on_loading_changed(self, wv, _pspec):
        if wv is not self._current_wv():
            return
        self.spinner.start() if wv.get_property("is-loading") else self.spinner.stop()

    def _on_title_changed(self, wv, _pspec, entry: TabEntry):
        title = wv.get_title()
        if title:
            entry.page.set_title(title)
            entry.label_widget.set_label(title)   # keep our custom button in sync

    def _on_uri_changed(self, wv, _pspec):
        if wv is not self._current_wv():
            return
        self._highlight_active_app(wv.get_uri() or "")

    def _on_selected_page_changed(self, tab_view, _pspec):
        wv = self._current_wv()
        if not wv:
            self.spinner.stop()
            return
        self.spinner.start() if wv.get_property("is-loading") else self.spinner.stop()
        self._refresh_tab_buttons()   # syncs both tab strip buttons and header app buttons

    def _on_close_page(self, tab_view, page):
        entry = self._all_tabs.pop(page, None)
        if entry:
            self._remove_tab_button(entry)
            if entry.track_label:
                self._named_tabs.pop(entry.track_label, None)
            if entry.wv is self._root_wv:
                self._root_wv = None
                for e in self._all_tabs.values():
                    self._root_wv = e.wv
                    break
            try:
                entry.wv.try_close()
            except Exception:
                pass

        tab_view.close_page_finish(page, True)
        if tab_view.get_n_pages() == 0:
            self.get_application().quit()
        return True

    def _on_wv_create(self, wv, _nav_action):
        """target="_blank" links -> new untracked tab."""
        new_wv = self._make_webview(related_wv=wv)
        entry_ref = [None]
        btn, lbl  = self._make_tab_button("New Tab", entry_ref)
        page      = self.tab_view.append(new_wv)
        page.set_title("New Tab")
        entry     = TabEntry(page, new_wv, btn, lbl)
        entry_ref[0] = entry

        self._all_tabs[page] = entry
        self._add_tab_button(entry)

        new_wv.connect("notify::is-loading", self._on_loading_changed)
        new_wv.connect("notify::title",      self._on_title_changed, entry)
        new_wv.connect("notify::uri",        self._on_uri_changed)
        new_wv.connect("create",             self._on_wv_create)

        self.tab_view.set_selected_page(page)
        return new_wv

    def _on_create_window(self, _tab_view, *_):
        return None

    def _on_key_pressed(self, _ctrl, keyval, _keycode, state):
        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
        wv   = self._current_wv()

        if ctrl:
            if keyval in (Gdk.KEY_plus, Gdk.KEY_equal) and wv:
                wv.set_zoom_level(min(wv.get_zoom_level() + 0.1, 4.0)); return True
            if keyval == Gdk.KEY_minus and wv:
                wv.set_zoom_level(max(wv.get_zoom_level() - 0.1, 0.25)); return True
            if keyval == Gdk.KEY_0 and wv:
                wv.set_zoom_level(1.0); return True
            if keyval == Gdk.KEY_t:
                self._open_tab("https://www.office.com", "Office", track=False); return True
            if keyval == Gdk.KEY_w:
                page = self.tab_view.get_selected_page()
                if page: self.tab_view.close_page(page)
                return True
            if keyval == Gdk.KEY_r and wv:
                wv.reload(); return True
            if keyval == Gdk.KEY_F5 and wv:
                wv.reload_bypass_cache(); return True

        if keyval == Gdk.KEY_F5 and wv:
            wv.reload(); return True

        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Office Online GTK  |  engine: WebKit 6.0 (GTK4-native)")
    app = OfficeApp()
    app.run(None)
