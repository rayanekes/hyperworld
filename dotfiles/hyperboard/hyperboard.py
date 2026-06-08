#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║         HYPERBOARD — Dashboard HYPERWORLD               ║
║   GTK4 + WebKit2 — Overlay plein écran animé           ║
║   Touche Super → ouvre / referme                        ║
╚══════════════════════════════════════════════════════════╝

Dépendances :
    sudo pacman -S python-gobject webkit2gtk-4.1 gtk4
    pip install requests feedparser
"""

import gi
gi.require_version("Gtk",        "4.0")
gi.require_version("WebKit",     "6.0")
gi.require_version("GtkLayerShell", "0.1")

import sys, os, json, threading, subprocess, time
from pathlib import Path
from gi.repository import Gtk, WebKit, GLib, Gdk, GtkLayerShell

BOARD_DIR = Path(__file__).parent.resolve()
HOME      = Path.home()


class HyperBoard(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.visible = False
        self._build_window()
        self._build_webview()
        self._setup_layer_shell()
        self._connect_signals()

    # ── Fenêtre Wayland (layer shell) ──────────────────────
    def _build_window(self):
        self.set_default_size(
            Gdk.Display.get_default().get_monitors().get_item(0).get_geometry().width,
            Gdk.Display.get_default().get_monitors().get_item(0).get_geometry().height,
        )
        self.set_decorated(False)
        self.set_resizable(False)

    def _setup_layer_shell(self):
        """Configure comme overlay Wayland au-dessus de tout"""
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP,    True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT,   True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT,  True)
        GtkLayerShell.set_exclusive_zone(self, -1)

    def _build_webview(self):
        """WebKit2 pour le rendu HTML/CSS/JS premium"""
        self.webview = WebKit.WebView()

        # Fond transparent pour le glassmorphism
        self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))

        # Paramètres WebKit
        settings = self.webview.get_settings()
        settings.set_enable_javascript(True)
        settings.set_enable_developer_extras(False)
        settings.set_hardware_acceleration_policy(
            WebKit.HardwareAccelerationPolicy.ALWAYS
        )

        # Gestionnaire de messages JS → Python
        self.webview.get_user_content_manager().connect(
            "script-message-received::hyperboard",
            self._on_js_message
        )
        self.webview.get_user_content_manager().register_script_message_handler(
            "hyperboard", None
        )

        self.set_child(self.webview)
        self._load_board()

    def _load_board(self):
        """Charge index.html avec les données système injectées"""
        html_path = BOARD_DIR / "index.html"
        if html_path.exists():
            self.webview.load_uri(f"file://{html_path}")
        else:
            self.webview.load_html(self._fallback_html(), "file:///")

    def _connect_signals(self):
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key)
        self.add_controller(key_ctrl)

    # ── Gestion des touches ─────────────────────────────────
    def _on_key(self, ctrl, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.hide_board()
            return True
        return False

    # ── Messages JavaScript → Python ────────────────────────
    def _on_js_message(self, manager, result):
        """Reçoit les commandes envoyées depuis JS"""
        msg = result.get_js_value().to_string()
        try:
            data = json.loads(msg)
            action = data.get("action", "")

            if action == "close":
                self.hide_board()

            elif action == "launch":
                app = data.get("app", "")
                if app:
                    subprocess.Popen(app.split(), stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    self.hide_board()

            elif action == "world":
                world = data.get("world", "prog")
                script = HOME / ".local/bin/world-switch.sh"
                subprocess.Popen(["bash", str(script), world])
                self.hide_board()

            elif action == "axiom":
                script = HOME / ".local/bin/axiom-launch.sh"
                subprocess.Popen(["bash", str(script)])
                self.hide_board()

            elif action == "get_data":
                # JS demande les données fraîches → on les envoie
                threading.Thread(target=self._fetch_and_send_data, daemon=True).start()

        except json.JSONDecodeError:
            pass

    def _fetch_and_send_data(self):
        """Récupère news + stats système et les envoie à JS"""
        data = {
            "system":   self._get_system_stats(),
            "news":     self._get_tech_news(),
            "games":    self._get_game_suggestions(),
            "weather":  self._get_weather(),
            "music":    self._get_now_playing(),
            "world":    self._get_current_world(),
        }
        payload = json.dumps(data, ensure_ascii=False).replace("'", "\\'")
        GLib.idle_add(
            self.webview.evaluate_javascript,
            f"window.receiveData({payload})",
            -1, None, None, None
        )

    # ── Données système ─────────────────────────────────────
    def _get_system_stats(self) -> dict:
        try:
            import psutil
            cpu  = psutil.cpu_percent(interval=0.3)
            ram  = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            bat  = psutil.sensors_battery()
            # GPU via nvidia-smi
            gpu_raw = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip().split(", ")
            return {
                "cpu_pct":   cpu,
                "ram_used":  round(ram.used / 1e9, 1),
                "ram_total": round(ram.total / 1e9, 1),
                "ram_pct":   ram.percent,
                "disk_pct":  disk.percent,
                "battery":   bat.percent if bat else None,
                "charging":  bat.power_plugged if bat else None,
                "gpu_temp":  gpu_raw[0] if len(gpu_raw) > 0 else "?",
                "gpu_pct":   gpu_raw[1] if len(gpu_raw) > 1 else "?",
                "gpu_mem":   f"{gpu_raw[2]}/{gpu_raw[3]} MB" if len(gpu_raw) > 3 else "?",
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_tech_news(self) -> list:
        """Hacker News Top Stories — API gratuite, sans clé"""
        try:
            import urllib.request, json
            # Top 8 stories
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            with urllib.request.urlopen(url, timeout=5) as r:
                ids = json.loads(r.read())[:8]
            stories = []
            for sid in ids:
                with urllib.request.urlopen(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=3
                ) as r:
                    item = json.loads(r.read())
                    stories.append({
                        "title": item.get("title", ""),
                        "url":   item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "score": item.get("score", 0),
                        "by":    item.get("by", ""),
                    })
            return stories
        except Exception:
            return [{"title": "Connexion non disponible", "url": "#", "score": 0, "by": ""}]

    def _get_game_suggestions(self) -> list:
        """Suggestions de jeux selon le monde actif + bibliothèque Steam"""
        world = self._get_current_world()
        # Jeux recommandés selon le monde
        suggestions = {
            "gaming": [
                {"name": "Red Dead Redemption 2",    "genre": "Action/Adventure", "emoji": "🤠"},
                {"name": "Genshin Impact",            "genre": "RPG/Open World",   "emoji": "⚔️"},
                {"name": "PES / eFootball",           "genre": "Sport",            "emoji": "⚽"},
                {"name": "Assassin's Creed Mirage",  "genre": "Action",           "emoji": "🗡️"},
            ],
            "cybersec": [
                {"name": "Hacknet",                   "genre": "Hacking Sim",      "emoji": "💻"},
                {"name": "NITE Team 4",               "genre": "ARG/Hacking",      "emoji": "🔐"},
                {"name": "Cyberpunk 2077",            "genre": "RPG/Cyber",        "emoji": "🌆"},
                {"name": "Watch Dogs 2",              "genre": "Hacking/Action",   "emoji": "📡"},
            ],
            "prog": [
                {"name": "Human Resource Machine",   "genre": "Puzzle/Code",      "emoji": "🤖"},
                {"name": "TIS-100",                   "genre": "Assembly Puzzle",  "emoji": "⚙️"},
                {"name": "Shenzhen I/O",              "genre": "PCB Design",       "emoji": "🔌"},
                {"name": "SpaceChem",                 "genre": "Logic/Puzzle",     "emoji": "🧪"},
            ],
        }
        return suggestions.get(world, suggestions["gaming"])

    def _get_weather(self) -> dict:
        """Météo depuis wttr.in — gratuit, sans API key"""
        try:
            import urllib.request, json
            with urllib.request.urlopen(
                "https://wttr.in/Algiers?format=j1", timeout=4
            ) as r:
                data = json.loads(r.read())
                current = data["current_condition"][0]
                return {
                    "temp_c":  current["temp_C"],
                    "desc":    current["weatherDesc"][0]["value"],
                    "feels":   current["FeelsLikeC"],
                    "humidity": current["humidity"],
                }
        except Exception:
            return {"temp_c": "?", "desc": "Indisponible", "feels": "?", "humidity": "?"}

    def _get_now_playing(self) -> dict:
        """Musique en cours via playerctl"""
        try:
            def pc(cmd):
                r = subprocess.run(["playerctl"] + cmd, capture_output=True, text=True, timeout=2)
                return r.stdout.strip()
            return {
                "title":  pc(["metadata", "title"]),
                "artist": pc(["metadata", "artist"]),
                "status": pc(["status"]),
            }
        except Exception:
            return {"title": "", "artist": "", "status": "Stopped"}

    def _get_current_world(self) -> str:
        try:
            r = subprocess.run(["hyprctl", "activeworkspace", "-j"],
                               capture_output=True, text=True, timeout=2)
            ws_id = json.loads(r.stdout).get("id", 7)
            if ws_id <= 3:   return "gaming"
            if ws_id <= 6:   return "cybersec"
            return "prog"
        except Exception:
            return "prog"

    # ── Affichage / Masquage ────────────────────────────────
    def show_board(self):
        self.present()
        self.visible = True
        # Demander les données fraîches au JS
        self.webview.evaluate_javascript(
            "window.onBoardOpen && window.onBoardOpen()",
            -1, None, None, None
        )
        # Envoyer les données en arrière-plan
        threading.Thread(target=self._fetch_and_send_data, daemon=True).start()

    def hide_board(self):
        self.webview.evaluate_javascript(
            "window.onBoardClose && window.onBoardClose()",
            -1, None, None, None
        )
        GLib.timeout_add(350, self.hide)  # attendre l'animation de fermeture
        self.visible = False

    def toggle(self):
        if self.visible:
            self.hide_board()
        else:
            self.show_board()

    def _fallback_html(self) -> str:
        return "<html><body style='background:#0d1117;color:#A78BFA;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0'><h1>HYPERBOARD</h1></body></html>"


# ── Application principale ──────────────────────────────────
class HyperBoardApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="xyz.hyperworld.hyperboard")
        self.board = None

    def do_activate(self):
        if not self.board:
            self.board = HyperBoard(self)

        # IPC via fichier signal
        signal_file = Path("/tmp/hyperboard-toggle")

        def watch_signal():
            while True:
                if signal_file.exists():
                    signal_file.unlink()
                    GLib.idle_add(self.board.toggle)
                time.sleep(0.1)

        threading.Thread(target=watch_signal, daemon=True).start()
        # Ouvrir immédiatement si lancé avec --toggle
        if "--toggle" in sys.argv:
            self.board.show_board()

    def do_startup(self):
        Gtk.Application.do_startup(self)


if __name__ == "__main__":
    app = HyperBoardApp()
    app.run(sys.argv)
