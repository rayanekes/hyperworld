#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  HYPERWORLD — get-wallpapers.sh
#  Télécharge des wallpapers pour les 3 mondes
#  via des sources libres (Unsplash, Wallhaven)
# ══════════════════════════════════════════════════════════

set -euo pipefail

WALLPAPER_DIR="$HOME/hyperworld/dotfiles/wallpapers"
mkdir -p "$WALLPAPER_DIR"

GRN='\033[92m'; CYN='\033[96m'; YLW='\033[93m'; R='\033[0m'
ok()   { echo -e "  ${GRN}✓${R}  $*"; }
info() { echo -e "  ${CYN}→${R}  $*"; }
warn() { echo -e "  ${YLW}⚠${R}  $*"; }

echo -e "\n${CYN}  ═══ HYPERWORLD — Téléchargement des Wallpapers ═══${R}\n"

# ── Fonction de téléchargement avec fallback ───────────────
download_wallpaper() {
    local name="$1"
    local url="$2"
    local dest="$WALLPAPER_DIR/$name.jpg"

    if [[ -f "$dest" ]]; then
        ok "$name.jpg déjà présent"
        return 0
    fi

    info "Téléchargement : $name..."
    if wget -q --show-progress -O "$dest" "$url" 2>&1; then
        # Vérifier que c'est bien une image
        if file "$dest" | grep -qE "image|JPEG|PNG"; then
            ok "$name.jpg téléchargé"
        else
            rm -f "$dest"
            warn "$name : fichier invalide, sera généré"
            generate_fallback "$name"
        fi
    else
        warn "$name : échec téléchargement, génération fallback..."
        generate_fallback "$name"
    fi
}

# ── Fallback : génération d'un wallpaper couleur via ImageMagick ──
generate_fallback() {
    local name="$1"
    local dest="$WALLPAPER_DIR/$name.jpg"

    if ! command -v convert &>/dev/null; then
        warn "ImageMagick non installé, wallpaper par défaut utilisé"
        return
    fi

    case "$name" in
        gaming)
            # Gradient magenta → violet → noir
            convert -size 1920x1080 \
                gradient:'#FF006E-#080010' \
                -set colorspace sRGB \
                "$dest" 2>/dev/null && ok "Wallpaper Gaming généré (gradient)"
            ;;
        cybersec)
            # Fond noir pur avec bruit subtil
            convert -size 1920x1080 \
                xc:'#000000' \
                +noise Uniform \
                -evaluate Multiply 0.03 \
                -colorize 0,50,0 \
                "$dest" 2>/dev/null && ok "Wallpaper Cybersec généré (matrix)"
            ;;
        prog)
            # Gradient bleu profond → ardoise
            convert -size 1920x1080 \
                gradient:'#0D1117-#1E3A5F' \
                "$dest" 2>/dev/null && ok "Wallpaper Prog généré (deep space)"
            ;;
        lockscreen)
            convert -size 1920x1080 \
                gradient:'#0D1117-#080010' \
                "$dest" 2>/dev/null && ok "Wallpaper Lockscreen généré"
            ;;
    esac
}

# ══════════════════════════════════════════════════════════
#  TÉLÉCHARGEMENTS
#  Sources : Unsplash (libre), fallback ImageMagick
# ══════════════════════════════════════════════════════════

# ── 🎮 GAMING — Cyberpunk / Neon City ────────────────────
# Unsplash — ville de nuit, néons
download_wallpaper "gaming" \
    "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1920&q=95&fit=crop"

# ── 🛡️ CYBERSEC — Dark / Code / Matrix ───────────────────
# Unsplash — code sombre
download_wallpaper "cybersec" \
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=95&fit=crop"

# ── 🔬 PROG — Espace / Nébuleuse ─────────────────────────
# Unsplash — nébuleuse spatiale
download_wallpaper "prog" \
    "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1920&q=95&fit=crop"

# ── 🔒 LOCKSCREEN — Sombre abstrait ──────────────────────
download_wallpaper "lockscreen" \
    "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&q=95&fit=crop"

# ── Copier le lockscreen dans la config Hyprland ──────────
HYPR_LOCK="$HOME/.config/hypr/lockscreen.jpg"
if [[ -f "$WALLPAPER_DIR/lockscreen.jpg" ]]; then
    cp "$WALLPAPER_DIR/lockscreen.jpg" "$HYPR_LOCK" 2>/dev/null || true
    ok "Lockscreen copié dans ~/.config/hypr/"
fi

echo -e "\n${GRN}  ✓ Wallpapers prêts dans : $WALLPAPER_DIR${R}"
echo -e "  → gaming.jpg | cybersec.jpg | prog.jpg | lockscreen.jpg\n"

# ── Appliquer le wallpaper Prog immédiatement si Hyprland tourne ──
if command -v swww &>/dev/null && pgrep -x Hyprland &>/dev/null; then
    info "Application du wallpaper Prog..."
    swww img "$WALLPAPER_DIR/prog.jpg" \
        --transition-type fade \
        --transition-duration 1.0 \
        --transition-fps 60 2>/dev/null || true
    ok "Wallpaper appliqué"
fi
