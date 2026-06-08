#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  HYPERWORLD — hypersettings.sh
#  Centre de contrôle unifié — mieux qu'Android & macOS
#
#  Agrège : Store, Apps, Permissions, Ressources,
#           Nettoyage, Apparence, Audio, Réseau, Bluetooth,
#           Snapshots, Démarrage, Dotfiles
# ══════════════════════════════════════════════════════════

ROFI_THEME="$HOME/.config/rofi/hypersettings.rasi"

# ── Entrées du menu (emoji + label + commande) ─────────────
declare -A COMMANDS
declare -a MENU_ITEMS

add_item() {
    local label="$1"
    local cmd="$2"
    MENU_ITEMS+=("$label")
    COMMANDS["$label"]="$cmd"
}

# ── 🛍️ Store & Paquets ─────────────────────────────────────
add_item "🛍️  Store (AUR + Flatpak + AppImage)"   "bauh"
add_item "📦  Gestionnaire Flatpak (Warehouse)"    "flatpak run io.github.flattool.Warehouse"
add_item "🔄  Mises à jour système"                "kitty -e bash -c 'paru -Syu; echo; read -p \"Entrée pour fermer\"'"

# ── 🔐 Permissions ──────────────────────────────────────────
add_item "🔐  Permissions Flatpak (Flatseal)"      "flatpak run com.github.tchx84.Flatseal"
add_item "🛡️  Firejail Profiles"                  "kitty -e bash -c 'firecfg --list; read -p \"Entrée\"'"

# ── ⚡ Ressources & Performances ────────────────────────────
add_item "⚡  Ressources par app (Mission Center)" "flatpak run io.missioncenter.MissionCenter"
add_item "📊  Moniteur système (btop)"             "kitty -e btop"
add_item "🎮  GPU (nvidia-smi live)"              "kitty -e bash -c 'watch -n1 nvidia-smi; read'"
add_item "🌡️  Températures"                       "kitty -e bash -c 'watch -n2 sensors; read'"

# ── 🧹 Nettoyage & Maintenance ──────────────────────────────
add_item "🧹  Nettoyage & Services (Stacer)"      "stacer"
add_item "🗑️  Cache pacman (paccache)"            "kitty -e bash -c 'sudo paccache -r; echo \"✓ Cache nettoyé\"; read'"
add_item "📁  Dossier home (ncdu)"                "kitty -e ncdu $HOME"
add_item "💾  Disque (df)"                        "kitty -e bash -c 'df -h; read'"

# ── 🎨 Apparence ────────────────────────────────────────────
add_item "🎨  Thème GTK (nwg-look)"              "nwg-look"
add_item "🖥️  Moniteurs (wdisplays)"             "wdisplays"
add_item "🌈  Sélecteur couleur"                  "hyprpicker -a"
add_item "🖼️  Wallpaper aléatoire"               "bash $HOME/.local/bin/get-wallpapers.sh"

# ── 🔊 Audio ────────────────────────────────────────────────
add_item "🔊  Volume & Sorties (pavucontrol)"     "pavucontrol"
add_item "🎵  Égaliseur (EasyEffects)"            "flatpak run com.github.wwmm.easyeffects"
add_item "🎤  Micro & entrées"                    "pavucontrol --tab=2"

# ── 📡 Réseau ───────────────────────────────────────────────
add_item "📡  Réseau (nm-connection-editor)"      "nm-connection-editor"
add_item "🔒  VPN"                                "nm-connection-editor"
add_item "📶  WiFi (iwctl)"                       "kitty -e iwctl"
add_item "🌐  DNS & Proxy"                        "kitty -e bash -c 'cat /etc/resolv.conf; read'"

# ── 🔵 Bluetooth ────────────────────────────────────────────
add_item "🔵  Bluetooth (blueman)"               "blueman-manager"
add_item "🎧  Périphériques Bluetooth"           "kitty -e bash -c 'bluetoothctl devices; read'"

# ── 💾 Snapshots & Sécurité ─────────────────────────────────
add_item "💾  Snapshots BTRFS (Timeshift)"        "pkexec timeshift-gtk"
add_item "🗝️  Clés SSH & GPG"                    "kitty -e bash -c 'ls -la ~/.ssh; read'"
add_item "🔑  Gestionnaire de mots de passe"      "keepassxc"

# ── 🚀 Démarrage auto ───────────────────────────────────────
add_item "🚀  Services au démarrage"              "kitty -e bash -c 'systemctl --user list-unit-files --state=enabled; read'"
add_item "⏱️  Temps de boot"                     "kitty -e bash -c 'systemd-analyze blame | head -20; read'"

# ── ☁️ Google Drive & Cloud ────────────────────────────────
add_item "☁️  Google Drive (upload/download)"     "\$HOME/.local/bin/gdrive.sh"
add_item "🔄  Synchroniser Drive maintenant"       "\$HOME/.local/bin/gdrive.sh sync"
add_item "📸  Backup Google Photos"                "\$HOME/.local/bin/gdrive.sh photos"
add_item "📊  État de la connexion Drive"          "\$HOME/.local/bin/gdrive.sh status"
add_item "⚙️  Configurer compte Google"            "\$HOME/.local/bin/setup-gdrive.sh"

# ── 🌌 HYPERWORLD ───────────────────────────────────────────
add_item "🌌  Changer de Monde"                   "bash $HOME/.local/bin/world-switch.sh"
add_item "🔄  Recharger Hyprland"                 "hyprctl reload"
add_item "⌨️  Raccourcis clavier"                 "kitty -e less $HOME/.config/hypr/keybinds.conf"
add_item "📋  Logs AXIOM"                         "kitty -e bash -c 'tail -50 ~/.axiom/logs/axiom.log; read'"
add_item "🤖  AXIOM Status"                       "kitty -e bash -c 'systemctl --user status axiom.service; read'"

# ── Affichage Rofi ──────────────────────────────────────────
CHOICE=$(printf '%s\n' "${MENU_ITEMS[@]}" | \
    rofi -dmenu \
        -i \
        -p "⚙️  HyperSettings" \
        -theme "$ROFI_THEME" \
        -format s \
        2>/dev/null)

# Exécuter la commande choisie
if [[ -n "$CHOICE" ]] && [[ -n "${COMMANDS[$CHOICE]+_}" ]]; then
    CMD="${COMMANDS[$CHOICE]}"
    eval "$CMD" &
fi
