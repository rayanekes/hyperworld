#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 11 — Finalisation + vérifications
- Vérifie que tout est en place
- Active les services utilisateur
- Configure power-monitor au démarrage
- Rapport final
"""
import subprocess, os, shutil
from pathlib import Path

REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
HOME      = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
CONFIG    = HOME / ".config"
BIN       = HOME / ".local" / "bin"

def run(cmd: str, check: bool = True) -> int:
    print(f"  $ {cmd}")
    r = subprocess.run(cmd, shell=True, check=False)
    return r.returncode

def check_installed(cmd: str, name: str) -> bool:
    ok = shutil.which(cmd) is not None
    icon = "✓" if ok else "✗"
    color = "\033[92m" if ok else "\033[91m"
    print(f"  {color}{icon}\033[0m  {name}")
    return ok

def run_checks():
    print("\n  ── Vérifications système ──")
    checks = [
        ("hyprctl",      "Hyprland"),
        ("waybar",       "Waybar"),
        ("kitty",        "Kitty Terminal"),
        ("swww",         "swww (wallpaper)"),
        ("rofi",         "Rofi launcher"),
        ("notify-send",  "Notifications"),
        ("playerctl",    "Contrôle media"),
        ("btop",         "btop (monitoring)"),
        ("fastfetch",    "fastfetch"),
        ("lazygit",      "LazyGit"),
        ("nvidia-smi",   "Nvidia SMI"),
        ("steam",        "Steam"),
        ("code",         "VSCode"),
        ("nmap",         "Nmap"),
        ("wireshark",    "Wireshark"),
    ]
    passed = sum(1 for cmd, name in checks if check_installed(cmd, name))
    print(f"\n  Résultat : {passed}/{len(checks)} outils détectés")
    return passed

def enable_user_services():
    print("\n  ── Activation services utilisateur ──")
    services = [
        "pipewire", "pipewire-pulse", "wireplumber",
        "axiom",
    ]
    for svc in services:
        run(f"systemctl --user enable {svc} 2>/dev/null", check=False)
        print(f"  ✓ {svc}")

def setup_hyprland_autostart():
    print("\n  ── Autostart Hyprland ──")
    hypr_dir = CONFIG / "hypr"
    autostart = hypr_dir / "autostart.conf"
    if not autostart.exists():
        hypr_dir.mkdir(parents=True, exist_ok=True)
        autostart.write_text("""# HYPERWORLD — Autostart

# Fond d'écran (monde prog par défaut)
exec-once = swww-daemon
exec-once = swww img ~/hyperworld/dotfiles/wallpapers/prog.jpg

# Waybar
exec-once = waybar

# Notifications
exec-once = swaync

# Polkit (authentification graphique)
exec-once = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1

# Clipboard manager
exec-once = wl-paste --watch cliphist store

# Power monitor (AXIOM activation auto)
exec-once = ~/.local/bin/power-monitor.sh

# XDG portail
exec-once = dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP

# Spotify (si installé)
# exec-once = flatpak run com.spotify.Client
""")
        print("  ✓ autostart.conf créé")
    else:
        print("  ✓ autostart.conf déjà existant")

def create_readme_installed():
    readme = HOME / "HYPERWORLD_INSTALLED.md"
    readme.write_text(f"""# ✅ HYPERWORLD — Installation Complète

## Raccourcis Clés

| Raccourci | Action |
|---|---|
| `Super + F1` | Monde Gaming 🎮 |
| `Super + F2` | Monde Cybersec 🛡️ |
| `Super + F3` | Monde Prog 🔬 |
| `Super` | Vue globale toutes apps |
| `Super + A` | Invoquer AXIOM |
| `Super + T` | Ouvrir terminal |
| `Super + Q` | Fermer fenêtre |
| `Super + M` | Quitter Hyprland |

## Répertoires importants

- Config Hyprland : `~/.config/hypr/`
- Config Waybar   : `~/.config/waybar/`
- AXIOM           : `~/.axiom/`
- Scripts         : `~/.local/bin/`
- Repo            : `~/hyperworld/`

## AXIOM

- Démarre automatiquement quand le chargeur est branché
- Invocation manuelle : `Super + A`
- Modèles dans : `~/.axiom/models/`
""")
    print(f"  ✓ Guide rapide créé : {readme}")

def final_fc_cache():
    run("fc-cache -fv > /dev/null 2>&1")
    print("  ✓ Cache fonts mis à jour")

def final_xdg_dirs():
    run("xdg-user-dirs-update")
    print("  ✓ Dossiers XDG mis à jour")

if __name__ == "__main__":
    print("\n  ═══ MODULE 11 : FINALISATION ═══\n")
    enable_user_services()
    setup_hyprland_autostart()
    final_fc_cache()
    final_xdg_dirs()
    create_readme_installed()
    passed = run_checks()
    print(f"""
  ══════════════════════════════════════════
    ✓  HYPERWORLD — SETUP TERMINÉ !
  ══════════════════════════════════════════
    {passed} outils vérifiés
    
    → Redémarre et sélectionne Hyprland dans SDDM
    → Super+F1/F2/F3 pour changer de monde
    → Super+A pour invoquer AXIOM
  ══════════════════════════════════════════
    """)
