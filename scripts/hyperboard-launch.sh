#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  HYPERBOARD — hyperboard-launch.sh
#  Lance le daemon HyperBoard ou envoie le signal toggle
# ══════════════════════════════════════════════════════════

BOARD_DIR="$HOME/hyperworld/dotfiles/hyperboard"
SIGNAL="/tmp/hyperboard-toggle"
PID_FILE="/tmp/hyperboard.pid"

# Vérifier si le daemon tourne
is_running() {
    [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null
}

if is_running; then
    # Daemon déjà actif → toggle via signal fichier
    touch "$SIGNAL"
else
    # Lancer le daemon HyperBoard en arrière-plan
    python "$BOARD_DIR/hyperboard.py" --toggle &
    echo $! > "$PID_FILE"
fi
