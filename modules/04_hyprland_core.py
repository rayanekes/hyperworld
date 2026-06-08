#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 04 — Hyprland Core + Stack Wayland complète
- Hyprland + portails XDG
- SDDM (display manager)
- swww, hyprlock, hypridle, swaync
- rofi-wayland, kitty
- Fonts + Flatpak + utils premium
"""
import subprocess, os, shutil
from pathlib import Path

REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
HOME      = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER      = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_hyprland_stack():
    print("\n  ── Hyprland + composants Wayland ──")
    pkgs = [
        "hyprland", "xdg-desktop-portal-hyprland",
        "xdg-desktop-portal-gtk", "xdg-desktop-portal",
        "waybar", "swww", "hyprlock", "hypridle",
        "hyprpaper", "hyprpicker", "swaync", "rofi-wayland",
        "kitty", "polkit", "polkit-gnome",
        "xdg-user-dirs", "xdg-utils",
        "qt5-wayland", "qt6-wayland", "qt5ct", "qt6ct",
        "gtk3", "gtk4", "gvfs", "gvfs-mtp",
        "thunar", "thunar-archive-plugin",
        "wl-clipboard", "cliphist",
        "grim", "slurp", "swappy", "imv",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)

def install_sddm():
    print("\n  ── SDDM (Display Manager) ──")
    run("sudo pacman -S --noconfirm --needed sddm qt6-svg qt6-declarative")
    run("sudo systemctl enable sddm")

    # Config SDDM basique
    sddm_conf_dir = Path("/etc/sddm.conf.d")
    sddm_conf_dir.mkdir(parents=True, exist_ok=True)
    conf = """[Theme]
Current=hyprworld

[General]
DisplayServer=wayland
GreeterEnvironment=QT_WAYLAND_SHELL_INTEGRATION=layer-shell

[Autologin]
# Décommente pour autologin
# User=rayane
# Session=hyprland
"""
    tmp = Path("/tmp/sddm-hyperworld.conf")
    tmp.write_text(conf)
    run("sudo mv /tmp/sddm-hyperworld.conf /etc/sddm.conf.d/hyperworld.conf")
    print("  ✓ SDDM configuré")

def install_fonts():
    print("\n  ── Fonts (critiques pour l'interface) ──")
    pkgs = [
        "noto-fonts", "noto-fonts-emoji", "noto-fonts-cjk", "noto-fonts-extra",
        "ttf-liberation", "ttf-dejavu",
        "ttf-jetbrains-mono-nerd", "ttf-hack-nerd",
        "ttf-cascadia-code-nerd", "otf-font-awesome",
        "ttf-font-awesome", "ttf-nerd-fonts-symbols",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    # AUR fonts
    run("paru -S --noconfirm --needed ttf-orbitron", check=False)
    run("fc-cache -fv > /dev/null 2>&1")
    print("  ✓ Fonts installées")

def install_flatpak():
    print("\n  ── Flatpak + Flathub ──")
    run("sudo pacman -S --noconfirm --needed flatpak")
    run("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo", check=False)
    print("  ✓ Flatpak configuré")

def install_utils():
    print("\n  ── Utilitaires premium CLI ──")
    pkgs = [
        "btop", "fastfetch", "bat", "eza", "fzf", "fd",
        "ripgrep", "zoxide", "starship", "tmux", "lazygit",
        "jq", "yq", "playerctl", "mpv", "ffmpeg", "imagemagick",
        "file-roller", "brightnessctl", "ddcutil",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    print("  ✓ Utilitaires installés")

def configure_hyprland_session():
    print("\n  ── Fichier session Hyprland pour SDDM ──")
    session_dir = Path("/usr/share/wayland-sessions")
    session_dir.mkdir(parents=True, exist_ok=True)
    session = """[Desktop Entry]
Name=Hyprland
Comment=An intelligent dynamic tiling Wayland compositor
Exec=Hyprland
Type=Application
"""
    tmp = Path("/tmp/hyprland.desktop")
    tmp.write_text(session)
    run("sudo mv /tmp/hyprland.desktop /usr/share/wayland-sessions/hyprland.desktop")
    print("  ✓ Session Hyprland enregistrée")

def configure_zsh():
    print("\n  ── ZSH + Oh-My-Zsh + plugins ──")
    run("sudo pacman -S --noconfirm --needed zsh", check=False)
    run("paru -S --noconfirm --needed zsh-autosuggestions zsh-syntax-highlighting", check=False)
    # fzf-tab : complétion intelligente (100× mieux que la complétion basique)
    run("paru -S --noconfirm --needed zsh-fzf-tab", check=False)
    # Changer le shell par défaut
    run(f"sudo chsh -s /bin/zsh {USER}", check=False)
    # Installer Oh-My-Zsh silencieusement
    result = subprocess.run("test -d ~/.oh-my-zsh", shell=True)
    if result.returncode != 0:
        run('sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended', check=False)
    print("  ✓ ZSH + fzf-tab configurés")

def install_hyperboard_deps():
    print("\n  ── HyperBoard deps (GTK4 + WebKit) ──")
    pkgs = [
        "python-gobject",
        "webkit2gtk-4.1",
        "gtk-layer-shell",
        "libadwaita",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    # PEP 668 : pas de pip hors venv sur Arch — utiliser pacman
    run("sudo pacman -S --noconfirm --needed python-psutil python-requests", check=False)
    print("  ✓ HyperBoard deps installées")

if __name__ == "__main__":
    print("\n  ═══ MODULE 04 : HYPRLAND CORE ═══\n")
    install_hyprland_stack()
    install_sddm()
    install_fonts()
    install_flatpak()
    install_utils()
    configure_hyprland_session()
    configure_zsh()
    install_hyperboard_deps()
    print("\n  ✓ Stack Hyprland + Wayland installée !")
