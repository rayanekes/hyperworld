#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  HYPERWORLD — screenshot.sh
#  Gestionnaire de screenshots complet
#
#  Usage :
#    screenshot.sh area      → sélection zone  (Print)
#    screenshot.sh full      → écran entier    (Shift+Print)
#    screenshot.sh copy      → zone → presse-papier (Super+Print)
#    screenshot.sh window    → fenêtre active
#    screenshot.sh gallery   → ouvrir galerie
# ══════════════════════════════════════════════════════════

set -euo pipefail

MODE="${1:-area}"
SAVE_DIR="$HOME/Pictures/Screenshots"
TIMESTAMP=$(date +"%Y%m%d-%Hh%Mm%Ss")
FILENAME="$SAVE_DIR/hw-$TIMESTAMP.png"

# Créer le dossier si absent
mkdir -p "$SAVE_DIR"

# ── Fonction : notification avec miniature ─────────────────
notify_screenshot() {
    local file="$1"
    local size
    size=$(du -h "$file" 2>/dev/null | cut -f1)
    notify-send "📸 Screenshot" \
        "Sauvegardé : $(basename "$file") ($size)" \
        --icon="$file" \
        --urgency=low \
        --expire-time=3000 \
        --hint="string:image-path:$file"
}

# ── Modes ──────────────────────────────────────────────────
case "$MODE" in

    # Zone sélectionnée → swappy (annotation)
    area)
        REGION=$(slurp -d 2>/dev/null) || exit 0
        grim -g "$REGION" - | \
            swappy -f - -o "$FILENAME"
        [[ -f "$FILENAME" ]] && {
            wl-copy < "$FILENAME"
            notify_screenshot "$FILENAME"
        }
        ;;

    # Écran entier → swappy
    full)
        grim "$FILENAME"
        swappy -f "$FILENAME" -o "$FILENAME"
        [[ -f "$FILENAME" ]] && {
            wl-copy < "$FILENAME"
            notify_screenshot "$FILENAME"
        }
        ;;

    # Zone → presse-papier uniquement (sans annotation)
    copy)
        REGION=$(slurp -d 2>/dev/null) || exit 0
        grim -g "$REGION" - | wl-copy
        notify-send "📋 Screenshot copié" \
            "Dans le presse-papier (pas sauvegardé)" \
            --urgency=low --expire-time=2000
        ;;

    # Fenêtre active uniquement
    window)
        # Récupérer la géométrie de la fenêtre active via hyprctl
        WIN_JSON=$(hyprctl activewindow -j 2>/dev/null)
        X=$(echo "$WIN_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['at'][0])")
        Y=$(echo "$WIN_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['at'][1])")
        W=$(echo "$WIN_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['size'][0])")
        H=$(echo "$WIN_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['size'][1])")
        grim -g "${X},${Y} ${W}x${H}" - | \
            swappy -f - -o "$FILENAME"
        [[ -f "$FILENAME" ]] && {
            wl-copy < "$FILENAME"
            notify_screenshot "$FILENAME"
        }
        ;;

    # Galerie des screenshots (via fzf + miniature imv)
    gallery)
        if [[ -z "$(ls -A "$SAVE_DIR"/*.png 2>/dev/null)" ]]; then
            notify-send "📸 Galerie" "Aucun screenshot trouvé" --urgency=low
            exit 0
        fi

        # Afficher les screenshots avec fzf + aperçu
        SELECTED=$(ls -t "$SAVE_DIR"/*.png 2>/dev/null | \
            fzf --reverse \
                --border=rounded \
                --preview='kitty +kitten icat --clear --transfer-mode=memory --place="${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}@0x0" {}' \
                --preview-window=right:60% \
                --header="Entrée: ouvrir | Ctrl+D: supprimer | Ctrl+Y: copier" \
                --bind "ctrl-d:execute(rm {})+reload(ls -t $SAVE_DIR/*.png 2>/dev/null || true)" \
                --bind "ctrl-y:execute-silent(wl-copy < {})" \
                --prompt="📸 Screenshots > " \
                2>/dev/null) || exit 0

        # Ouvrir avec imv ou eog si sélectionné
        if [[ -f "$SELECTED" ]]; then
            if command -v imv &>/dev/null; then
                imv "$SELECTED"
            elif command -v eog &>/dev/null; then
                eog "$SELECTED"
            else
                xdg-open "$SELECTED"
            fi
        fi
        ;;

    *)
        echo "Usage: screenshot.sh [area|full|copy|window|gallery]"
        exit 1
        ;;
esac
