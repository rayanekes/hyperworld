#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 05 — Système Multi-Monde
- Scripts de changement de monde
- world-switch.sh (animations Hyprland)
- global-overview (vue Super)
- power-monitor.sh (détection secteur)
"""
import subprocess, os
from pathlib import Path

REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
HOME      = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
BIN       = HOME / ".local" / "bin"

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def write_exec(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(0o755)
    print(f"  ✓ {path}")

def create_world_switch():
    write_exec(BIN / "world-switch.sh", """#!/bin/bash
# HYPERWORLD — Changement de monde avec animations
# Usage: world-switch.sh [gaming|cybersec|prog]

WORLD="${1:-gaming}"
REPO="$HOME/hyperworld"
CONFIG="$HOME/.config"

# ── Fonction de transition ────────────────────────────────────
switch_world() {
    local world="$1"
    
    # 1. Animation de sortie (flash + fade)
    hyprctl dispatch dpms off 2>/dev/null
    sleep 0.1
    hyprctl dispatch dpms on 2>/dev/null
    
    # 2. Changer le fond d'écran avec transition animée
    case "$world" in
        gaming)
            TARGET_WS=1
            WALLPAPER="$REPO/dotfiles/wallpapers/gaming.jpg"
            WAYBAR_WORLD="gaming"
            KITTY_CONF="gaming.conf"
            ;;
        cybersec)
            TARGET_WS=4
            WALLPAPER="$REPO/dotfiles/wallpapers/cybersec.jpg"
            WAYBAR_WORLD="cybersec"
            KITTY_CONF="cybersec.conf"
            ;;
        prog)
            TARGET_WS=7
            WALLPAPER="$REPO/dotfiles/wallpapers/prog.jpg"
            WAYBAR_WORLD="prog"
            KITTY_CONF="prog.conf"
            ;;
        *)
            echo "Usage: world-switch.sh [gaming|cybersec|prog]"
            exit 1
            ;;
    esac
    
    # 3. Transition fond d'écran (swww avec animation)
    if [ -f "$WALLPAPER" ]; then
        swww img "$WALLPAPER" \\
            --transition-type wave \\
            --transition-duration 0.8 \\
            --transition-fps 144 \\
            --transition-angle 45 \\
            --transition-step 90
    fi
    
    # 4. Appliquer la config Waybar du monde
    ln -sf "$REPO/dotfiles/waybar/$WAYBAR_WORLD/config.jsonc" "$CONFIG/waybar/config.jsonc"
    ln -sf "$REPO/dotfiles/waybar/$WAYBAR_WORLD/style.css" "$CONFIG/waybar/style.css"
    pkill waybar 2>/dev/null
    sleep 0.3
    waybar &
    
    # 5. Appliquer le thème Kitty du monde
    ln -sf "$REPO/dotfiles/kitty/$KITTY_CONF" "$CONFIG/kitty/kitty.conf"
    
    # 6. Naviguer vers le premier workspace du monde
    hyprctl dispatch workspace "$TARGET_WS"
    
    # 7. Notifier AXIOM du changement
    echo "WORLD_CHANGE:$world" > /tmp/axiom-events 2>/dev/null
    
    # 8. Notification visuelle
    notify-send "HYPERWORLD" "Monde activé : $(echo $world | tr '[:lower:]' '[:upper:]')" \\
        --icon=preferences-desktop --urgency=low
}

switch_world "$WORLD"
""")

def create_global_overview():
    write_exec(BIN / "global-overview.sh", """#!/bin/bash
# HYPERWORLD — Vue globale de toutes les apps (touche Super)
# Affiche TOUTES les fenêtres de TOUS les mondes

# Récupérer toutes les fenêtres ouvertes
WINDOWS=$(hyprctl clients -j | python3 -c "
import sys, json
clients = json.load(sys.stdin)
lines = []
for c in clients:
    ws = c.get('workspace', {}).get('id', '?')
    title = c.get('title', 'Inconnu')[:40]
    cls = c.get('class', '?')[:20]
    addr = c.get('address', '')
    
    # Associer workspace au monde
    if 1 <= int(str(ws)) <= 3:
        monde = '🎮 GAMING'
    elif 4 <= int(str(ws)) <= 6:
        monde = '🛡️ CYBERSEC'
    elif 7 <= int(str(ws)) <= 9:
        monde = '🔬 PROG'
    else:
        monde = '❓ AUTRE'
    
    lines.append(f'[{monde}] WS{ws} | {cls:<20} | {title}')

print('\n'.join(lines)) if lines else print('Aucune fenêtre ouverte')
")

# Afficher dans Rofi avec thème custom
CHOICE=$(echo "$WINDOWS" | rofi \\
    -dmenu \\
    -i \\
    -theme "$HOME/hyperworld/dotfiles/rofi/global-overview.rasi" \\
    -p "🌍 HYPERWORLD — Toutes les apps" \\
    -font "JetBrainsMono Nerd Font 12" \\
    -no-custom)

if [ -n "$CHOICE" ]; then
    # Extraire le workspace et focus la fenêtre
    WS=$(echo "$CHOICE" | grep -oP 'WS\K[0-9]+')
    TITLE=$(echo "$CHOICE" | sed 's/.*| //')
    
    if [ -n "$WS" ]; then
        hyprctl dispatch workspace "$WS"
        hyprctl dispatch focuswindow "title:$TITLE" 2>/dev/null
    fi
fi
""")

def create_power_monitor():
    write_exec(BIN / "power-monitor.sh", """#!/bin/bash
# HYPERWORLD — Surveillance alimentation
# Lance/arrête AXIOM selon secteur/batterie

monitor_power() {
    local prev_state=""
    
    while true; do
        # Vérifier si branché
        if cat /sys/class/power_supply/AC*/online 2>/dev/null | grep -q "1"; then
            state="online"
        else
            state="offline"
        fi
        
        if [ "$state" != "$prev_state" ]; then
            if [ "$state" = "online" ]; then
                systemctl --user start axiom.service 2>/dev/null
                notify-send "AXIOM" "Mode secteur — AXIOM activé" --icon=battery-full
            else
                systemctl --user stop axiom.service 2>/dev/null
                notify-send "AXIOM" "Mode batterie — AXIOM en veille" --icon=battery-low
            fi
            prev_state="$state"
        fi
        
        sleep 10
    done
}

monitor_power
""")

def create_axiom_launch():
    write_exec(BIN / "axiom-launch.sh", """#!/bin/bash
# HYPERWORLD — Invocation manuelle d'AXIOM
# Super+A ou appel depuis n'importe quel monde

AXIOM_DIR="$HOME/.axiom"
VENV="$AXIOM_DIR/venv"

# Si AXIOM daemon tourne → ouvrir l'interface
if systemctl --user is-active axiom.service > /dev/null 2>&1; then
    # Envoyer signal d'ouverture interface
    echo "UI_OPEN" > /tmp/axiom-events
else
    # Démarrer AXIOM en mode interactif direct
    kitty --class axiom-terminal \\
        --title "AXIOM — Assistant IA" \\
        --config "$HOME/.config/kitty/prog.conf" \\
        "$VENV/bin/python" "$AXIOM_DIR/axiom.py" --interactive
fi
""")

if __name__ == "__main__":
    print("\n  ═══ MODULE 05 : SYSTÈME MULTI-MONDE ═══\n")
    create_world_switch()
    create_global_overview()
    create_power_monitor()
    create_axiom_launch()
    print("\n  ✓ Scripts Multi-Monde créés !")
