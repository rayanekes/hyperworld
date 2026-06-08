#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════╗
# ║       HYPERWORLD — bootstrap.sh                         ║
# ║  Premier script à lancer sur un Arch Linux tout frais   ║
# ║                                                          ║
# ║  Usage (depuis le repo cloné) :                         ║
# ║    bash bootstrap.sh                                     ║
# ║                                                          ║
# ║  Ou en une ligne (sans avoir le repo) :                  ║
# ║    curl -fsSL https://raw.githubusercontent.com/         ║
# ║    TON_USER/hyperworld/main/bootstrap.sh | bash          ║
# ╚══════════════════════════════════════════════════════════╝

set -euo pipefail

# ── Couleurs ──────────────────────────────────────────────
R='\033[0m'
BOLD='\033[1m'
RED='\033[91m'
GRN='\033[92m'
YLW='\033[93m'
CYN='\033[96m'
MAG='\033[95m'

ok()   { echo -e "  ${GRN}✓${R}  $*"; }
info() { echo -e "  ${CYN}→${R}  $*"; }
warn() { echo -e "  ${YLW}⚠${R}  $*"; }
fail() { echo -e "  ${RED}✗${R}  $*"; exit 1; }

# ── Banner ────────────────────────────────────────────────
echo -e "${CYN}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║          HYPERWORLD — Bootstrap v1.0                     ║
║   Préparation du système avant install.py               ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${R}"

# ── Vérifications préliminaires ───────────────────────────
if [[ "$EUID" -eq 0 ]]; then
    fail "Ne pas lancer en root. Lance avec ton utilisateur normal (sudo sera demandé)."
fi

if ! command -v pacman &>/dev/null; then
    fail "Pacman introuvable. Ce script est pour Arch Linux uniquement."
fi

info "Système détecté : $(uname -r)"
info "Utilisateur : $USER"

# ── Étape 1 : Mise à jour des miroirs ────────────────────
echo -e "\n${BOLD}  [1/7] Optimisation des miroirs pacman${R}"
if command -v reflector &>/dev/null; then
    info "reflector déjà installé, mise à jour des miroirs..."
    sudo reflector \
        --country France,Germany,Spain \
        --age 12 \
        --protocol https \
        --sort rate \
        --save /etc/pacman.d/mirrorlist \
        2>/dev/null && ok "Miroirs optimisés" || warn "reflector échoué, miroirs existants conservés"
else
    info "Installation de reflector..."
    sudo pacman -Sy --noconfirm --needed reflector 2>/dev/null || true
fi

# ── Étape 2 : Mise à jour du système ─────────────────────
echo -e "\n${BOLD}  [2/7] Mise à jour du système${R}"
sudo pacman -Syu --noconfirm
ok "Système à jour"

# ── Étape 3 : Paquets essentiels avant install.py ────────
echo -e "\n${BOLD}  [3/7] Installation des paquets bootstrap${R}"
BOOTSTRAP_PKGS=(
    # ── Python (requis pour install.py) ──
    python
    python-pip
    python-setuptools
    python-wheel

    # ── Git (clone du repo) ──
    git
    git-lfs

    # ── Téléchargement ──
    wget
    curl

    # ── Compilation (requis pour paru + AUR) ──
    base-devel
    cmake
    make
    gcc
    g++

    # ── Outils essentiels ──
    sudo
    nano
    vim

    # ── Réseau (vérifié avant tout) ──
    networkmanager
    iwd

    # ── Crypto / TLS ──
    ca-certificates
    openssl

    # ── Process tools ──
    procps-ng
    psmisc

    # ── Compression ──
    tar
    zip
    unzip
    p7zip

    # ── Système ──
    usbutils
    pciutils
    lshw

    # ── Pour télécharger les modèles HuggingFace ──
    wget
    aria2   # téléchargement parallèle (fallback rapide)
)

info "Installation de ${#BOOTSTRAP_PKGS[@]} paquets bootstrap..."
sudo pacman -S --noconfirm --needed "${BOOTSTRAP_PKGS[@]}" 2>&1 | \
    grep -E "^(:: |installing|warning)" || true
ok "Paquets bootstrap installés"

# ── Étape 4 : Activer NetworkManager si pas déjà fait ────
echo -e "\n${BOLD}  [4/7] Activation NetworkManager${R}"
if ! systemctl is-active --quiet NetworkManager; then
    sudo systemctl enable --now NetworkManager
    ok "NetworkManager activé"
else
    ok "NetworkManager déjà actif"
fi

# ── Étape 5 : Vérifier la connexion internet ─────────────
echo -e "\n${BOLD}  [5/7] Vérification connexion internet${R}"
if ping -c 1 archlinux.org &>/dev/null; then
    ok "Connexion internet OK"
else
    fail "Pas de connexion internet. Connecte-toi d'abord (nmcli device wifi connect ...)"
fi

# ── Étape 6 : Cloner / mettre à jour le repo ─────────────
echo -e "\n${BOLD}  [6/7] Récupération du repo HYPERWORLD${R}"
REPO_DIR="$HOME/hyperworld"
REPO_URL="https://github.com/rayanekes/hyperworld.git"

if [[ -d "$REPO_DIR/.git" ]]; then
    info "Repo déjà cloné, mise à jour..."
    cd "$REPO_DIR"
    git pull --ff-only && ok "Repo à jour" || warn "Impossible de mettre à jour (modifications locales ?)"
elif [[ -d "$REPO_DIR" && -f "$REPO_DIR/install.py" ]]; then
    info "Fichiers trouvés dans $REPO_DIR (pas de .git, probablement copié)"
    ok "Utilisation des fichiers existants"
else
    info "Clonage depuis $REPO_URL..."
    if [[ "$REPO_URL" == *"rayanekes"* ]]; then
        warn "URL du repo non configurée !"
        echo -e "\n  ${MAG}Entre l'URL de ton repo GitHub :${R}"
        read -rp "  URL : " REPO_URL
    fi
    git clone "$REPO_URL" "$REPO_DIR"
    ok "Repo cloné dans $REPO_DIR"
fi
cd "$REPO_DIR"

# ── Étape 7 : Lancer install.py ──────────────────────────
echo -e "\n${BOLD}  [7/7] Démarrage de l'installation principale${R}"
echo -e "\n${CYN}  ════════════════════════════════════════════${R}"
echo -e "  ${BOLD}Tout est prêt. Lancement de install.py...${R}"
echo -e "${CYN}  ════════════════════════════════════════════${R}\n"

sleep 1
exec python "$REPO_DIR/install.py"
