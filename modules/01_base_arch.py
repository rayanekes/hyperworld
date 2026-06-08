#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 01 — Base Arch Linux
- Optimise les miroirs avec reflector
- Installe tous les paquets base + wayland
- Active multilib
- Installe paru (AUR helper)
- Active les services essentiels
"""

import subprocess, os, sys
from pathlib import Path

REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
HOME      = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def read_packages(file: str) -> list[str]:
    """Lit un fichier de paquets en ignorant commentaires et lignes vides"""
    path = REPO_ROOT / "packages" / file
    pkgs = []
    if not path.exists():
        print(f"  ⚠ {path} introuvable")
        return pkgs
    for line in path.read_text().splitlines():
        line = line.split("#")[0].strip()
        if line:
            pkgs.append(line)
    return pkgs

def optimize_mirrors():
    print("\n  ── Optimisation des miroirs pacman ──")
    run("sudo reflector --country France,Germany --age 12 --protocol https "
        "--sort rate --save /etc/pacman.d/mirrorlist", check=False)

def enable_multilib():
    print("\n  ── Activation de multilib ──")
    pacman_conf = Path("/etc/pacman.conf")
    content = pacman_conf.read_text()
    if "[multilib]" not in content or "#[multilib]" in content:
        content = content.replace("#[multilib]\n#Include", "[multilib]\nInclude")
        # Écriture via tee pour avoir les droits sudo
        tmp = Path("/tmp/pacman.conf.new")
        tmp.write_text(content)
        run("sudo mv /tmp/pacman.conf.new /etc/pacman.conf")
        run("sudo pacman -Sy")
        print("  ✓ multilib activé")
    else:
        print("  ✓ multilib déjà activé")

def install_paru():
    print("\n  ── Installation de paru (AUR helper) ──")
    result = subprocess.run("command -v paru", shell=True, capture_output=True)
    if result.returncode == 0:
        print("  ✓ paru déjà installé")
        return
    run("sudo pacman -S --noconfirm --needed git base-devel")
    run("git clone https://aur.archlinux.org/paru.git /tmp/paru")
    run("cd /tmp/paru && makepkg -si --noconfirm")
    run("rm -rf /tmp/paru")
    print("  ✓ paru installé")

def install_base_packages():
    print("\n  ── Installation des paquets base ──")
    pkgs = read_packages("base.txt")
    if pkgs:
        run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}")

def install_wayland_packages():
    print("\n  ── Installation Wayland + Hyprland Stack ──")
    pkgs = read_packages("wayland.txt")
    # Séparer les paquets AUR (commentés dans le fichier)
    pacman_pkgs = [p for p in pkgs if p]
    if pacman_pkgs:
        # Bug 3 fix : paru gère à la fois les repos officiels et AUR
        run(f"paru -S --noconfirm --needed {' '.join(pacman_pkgs)}", check=False)

def enable_services():
    print("\n  ── Activation des services système ──")
    services = [
        "NetworkManager",
        "bluetooth",
        "firewalld",
        "acpid",
        "fwupd",
        "thermald",
        "power-profiles-daemon",
        "sddm",
    ]
    for svc in services:
        run(f"sudo systemctl enable {svc}", check=False)
        print(f"  ✓ {svc}")

def configure_environment():
    print("\n  ── Configuration variables d'environnement Wayland/Nvidia ──")
    env_file = Path("/etc/environment")
    env_vars = """# HYPERWORLD — Wayland + Nvidia RTX 4050
LIBVA_DRIVER_NAME=nvidia
XDG_SESSION_TYPE=wayland
GBM_BACKEND=nvidia-drm
__GLX_VENDOR_LIBRARY_NAME=nvidia
NVD_BACKEND=direct
WLR_NO_HARDWARE_CURSORS=1
ELECTRON_OZONE_PLATFORM_HINT=auto
MOZ_ENABLE_WAYLAND=1
QT_QPA_PLATFORM=wayland
QT_AUTO_SCREEN_SCALE_FACTOR=1
SDL_VIDEODRIVER=wayland
CLUTTER_BACKEND=wayland
"""
    current = env_file.read_text() if env_file.exists() else ""
    if "HYPERWORLD" not in current:
        tmp = Path("/tmp/environment.new")
        tmp.write_text(current + "\n" + env_vars)
        run("sudo mv /tmp/environment.new /etc/environment")
        print("  ✓ Variables d'environnement configurées")
    else:
        print("  ✓ Variables déjà configurées")

def configure_pacman():
    print("\n  ── Configuration pacman (couleurs + téléchargement parallèle) ──")
    conf = Path("/etc/pacman.conf")
    content = conf.read_text()
    changes = False
    if "#Color" in content:
        content = content.replace("#Color", "Color\nILoveCandy")
        changes = True
    if "#ParallelDownloads" in content:
        content = content.replace("#ParallelDownloads = 5", "ParallelDownloads = 10")
        changes = True
    if changes:
        tmp = Path("/tmp/pacman.conf.mod")
        tmp.write_text(content)
        run("sudo mv /tmp/pacman.conf.mod /etc/pacman.conf")
        print("  ✓ pacman optimisé")

def setup_xdg_dirs():
    print("\n  ── Création des dossiers XDG utilisateur ──")
    run("xdg-user-dirs-update")
    # Créer les dossiers essentiels pour HYPERWORLD
    dirs = [
        HOME / ".config",
        HOME / ".local/bin",
        HOME / ".local/share/applications",
        HOME / ".axiom/models",
        HOME / ".axiom/whisper",
        HOME / ".axiom/piper",
        HOME / ".axiom/rag",
        HOME / ".axiom/logs",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  ✓ Dossiers créés")

if __name__ == "__main__":
    print("\n  ═══ MODULE 01 : BASE ARCH LINUX ═══\n")
    optimize_mirrors()
    configure_pacman()
    enable_multilib()
    install_base_packages()
    install_paru()
    install_wayland_packages()
    configure_environment()
    enable_services()
    setup_xdg_dirs()
    print("\n  ✓ Base Arch Linux configurée avec succès !")
