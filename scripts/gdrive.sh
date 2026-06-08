#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  HYPERWORLD — gdrive.sh
#  Interface Google Drive + Google Photos via rclone
#
#  Utilisation :
#    gdrive.sh          → menu Rofi interactif
#    gdrive.sh sync     → synchronisation rapide
#    gdrive.sh status   → état des syncs
# ══════════════════════════════════════════════════════════

set -euo pipefail

ROFI_THEME="$HOME/.config/rofi/hypersettings.rasi"
GDRIVE_REMOTE="gdrive"
GPHOTOS_REMOTE="gphotos"
LOG_FILE="$HOME/.local/share/hyperworld/gdrive-sync.log"
SYNC_DIR="$HOME/.config/gdrive-sync"

# Dossiers synchronisés automatiquement
SYNC_PAIRS=(
    "$HOME/Documents|$GDRIVE_REMOTE:Documents"
    "$HOME/Pictures/Screenshots|$GPHOTOS_REMOTE:album/HYPERWORLD"
    "$HOME/hyperworld|$GDRIVE_REMOTE:HYPERWORLD_Backup"
)

mkdir -p "$HOME/.local/share/hyperworld" "$(dirname $LOG_FILE)"

# ── Vérification rclone configuré ─────────────────────────
check_remote() {
    local remote="$1"
    rclone listremotes 2>/dev/null | grep -q "^${remote}:" && return 0
    notify-send "☁️ Google Drive" \
        "Remote '$remote' non configuré.\nLance : rclone config" \
        --urgency=critical
    kitty -e bash -c "
        echo '═══ Configuration rclone pour HYPERWORLD ═══'
        echo ''
        echo 'Tu vas configurer Google Drive + Google Photos.'
        echo 'Suis les instructions. Un navigateur va souvrir.'
        echo ''
        rclone config
        echo ''
        echo 'Configuration terminée. Ferme cette fenêtre.'
        read -p 'Appuie sur Entrée...'
    " &
    exit 1
}

# ── Notification avec progrès ──────────────────────────────
notify() {
    notify-send "☁️ Google Drive" "$1" --urgency="${2:-low}" --expire-time=4000
}

# ── Upload fichier ou dossier ──────────────────────────────
cmd_upload() {
    check_remote "$GDRIVE_REMOTE"

    # Choisir le fichier/dossier avec zenity ou yad
    local src
    if command -v zenity &>/dev/null; then
        src=$(zenity --file-selection --title="Choisir un fichier/dossier à uploader" 2>/dev/null) || exit 0
    else
        src=$(kitty -e bash -c "
            echo 'Chemin du fichier/dossier à uploader :'
            read -e path
            echo \$path
        " 2>/dev/null) || exit 0
    fi

    [[ -z "$src" ]] && exit 0

    # Choisir le dossier destination sur Drive
    local dst
    dst=$(rclone lsd "$GDRIVE_REMOTE:" --max-depth 2 2>/dev/null | \
        awk '{print $NF}' | \
        rofi -dmenu -p "📁 Dossier Drive destination" -theme "$ROFI_THEME" \
        2>/dev/null || echo "")

    [[ -z "$dst" ]] && dst=""

    notify "⬆️ Upload en cours...\n$(basename $src)"

    rclone copy "$src" "$GDRIVE_REMOTE:$dst" \
        --progress \
        --transfers 4 \
        --log-file "$LOG_FILE" \
        --log-level INFO \
        2>/dev/null

    notify "✅ Upload terminé !\n$(basename $src) → Drive/$dst"
}

# ── Télécharger depuis Drive ───────────────────────────────
cmd_download() {
    check_remote "$GDRIVE_REMOTE"

    # Lister les fichiers Drive dans fzf
    local remote_file
    remote_file=$(rclone ls "$GDRIVE_REMOTE:" --max-depth 3 2>/dev/null | \
        awk '{$1=""; print $0}' | sed 's/^ //' | \
        fzf --prompt="📥 Fichier Drive à télécharger > " \
            --header="Ctrl+C pour annuler" \
            --height=60% --border=rounded \
            2>/dev/null) || exit 0

    [[ -z "$remote_file" ]] && exit 0

    # Destination locale
    local dst_dir
    dst_dir=$(zenity --file-selection --directory \
        --title="Dossier de destination local" 2>/dev/null || echo "$HOME/Downloads")

    notify "⬇️ Téléchargement...\n$(basename $remote_file)"

    rclone copy "$GDRIVE_REMOTE:$remote_file" "$dst_dir/" \
        --progress \
        --log-file "$LOG_FILE" \
        2>/dev/null

    notify "✅ Téléchargé !\n$(basename $remote_file) → $dst_dir"
}

# ── Sync bidirectionnel d'un dossier ──────────────────────
cmd_sync_now() {
    check_remote "$GDRIVE_REMOTE"
    check_remote "$GPHOTOS_REMOTE"

    notify "🔄 Synchronisation en cours..."
    local errors=0

    for pair in "${SYNC_PAIRS[@]}"; do
        local local_dir="${pair%%|*}"
        local remote_dir="${pair##*|}"

        [[ ! -d "$local_dir" ]] && { mkdir -p "$local_dir"; }

        echo "[$(date)] Sync: $local_dir → $remote_dir" >> "$LOG_FILE"

        rclone sync "$local_dir" "$remote_dir" \
            --transfers 4 \
            --log-file "$LOG_FILE" \
            --log-level INFO \
            --exclude ".git/**" \
            --exclude "*.pyc" \
            --exclude "__pycache__/**" \
            --exclude "*.gguf" \
            --exclude "node_modules/**" \
            2>/dev/null || ((errors++))
    done

    if [[ $errors -eq 0 ]]; then
        notify "✅ Synchronisation complète !" low
    else
        notify "⚠️ Sync terminée avec $errors erreur(s)\nVoir : $LOG_FILE" normal
    fi
}

# ── Backup Google Photos ───────────────────────────────────
cmd_photos_backup() {
    check_remote "$GPHOTOS_REMOTE"

    local pics_dir="$HOME/Pictures"
    notify "📸 Backup Google Photos en cours..."

    rclone sync "$pics_dir" "$GPHOTOS_REMOTE:album/HYPERWORLD" \
        --transfers 4 \
        --include "*.jpg" --include "*.jpeg" --include "*.png" \
        --include "*.mp4" --include "*.mov" --include "*.mkv" \
        --log-file "$LOG_FILE" \
        --log-level INFO \
        2>/dev/null

    notify "✅ Photos sauvegardées sur Google Photos !"
}

# ── Voir les logs ──────────────────────────────────────────
cmd_logs() {
    kitty -e bash -c "tail -50 '$LOG_FILE'; read -p 'Entrée pour fermer...'"
}

# ── Gérer les remotes ──────────────────────────────────────
cmd_configure() {
    kitty -e bash -c "
        echo '══════════════════════════════════════'
        echo '  Configuration rclone HYPERWORLD'
        echo '══════════════════════════════════════'
        echo ''
        echo 'Remotes actuels :'
        rclone listremotes
        echo ''
        rclone config
        echo ''
        read -p 'Terminé. Entrée pour fermer...'
    "
}

# ── Statut de la sync auto ────────────────────────────────
cmd_status() {
    local gdrive_ok="❌ Non configuré"
    local gphotos_ok="❌ Non configuré"
    rclone listremotes 2>/dev/null | grep -q "^${GDRIVE_REMOTE}:" && gdrive_ok="✅ Connecté"
    rclone listremotes 2>/dev/null | grep -q "^${GPHOTOS_REMOTE}:" && gphotos_ok="✅ Connecté"

    local timer_status
    timer_status=$(systemctl --user is-active gdrive-sync.timer 2>/dev/null || echo "inactif")

    local last_sync
    last_sync=$(tail -5 "$LOG_FILE" 2>/dev/null | grep "Sync:" | tail -1 | awk '{print $1, $2}' || echo "Jamais")

    notify-send "☁️ État Google Drive" \
"Google Drive : $gdrive_ok
Google Photos : $gphotos_ok
Auto-sync : $timer_status
Dernière sync : $last_sync" \
        --expire-time=6000
}

# ── Menu Rofi ─────────────────────────────────────────────
case "${1:-menu}" in
    sync)   cmd_sync_now   ;;
    photos) cmd_photos_backup ;;
    status) cmd_status     ;;
    *)
        CHOICE=$(cat << 'EOF' | rofi -dmenu -p "☁️  Google Drive" -theme "$ROFI_THEME"
⬆️  Uploader un fichier / dossier
⬇️  Télécharger depuis Drive
🔄  Synchroniser maintenant
📸  Backup Google Photos
📊  Voir l'état de la sync
📋  Voir les logs
⚙️  Configurer / Ajouter un compte
🕐  Activer sync automatique
🛑  Désactiver sync automatique
EOF
        )

        case "$CHOICE" in
            "⬆️"*)  cmd_upload ;;
            "⬇️"*)  cmd_download ;;
            "🔄"*)  cmd_sync_now ;;
            "📸"*)  cmd_photos_backup ;;
            "📊"*)  cmd_status ;;
            "📋"*)  cmd_logs ;;
            "⚙️"*)  cmd_configure ;;
            "🕐"*)
                systemctl --user enable --now gdrive-sync.timer 2>/dev/null
                notify "✅ Sync automatique activée (toutes les 30 min)" ;;
            "🛑"*)
                systemctl --user disable --now gdrive-sync.timer 2>/dev/null
                notify "Sync automatique désactivée" ;;
        esac
        ;;
esac
