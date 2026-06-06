#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 06 — Applications Monde Gaming
- Steam, Lutris, Bottles (AUR), Heroic (AUR)
- GameMode, MangoHUD, Gamescope
- Wine + Proton GE (AUR)
- Discord (Flatpak)
"""
import subprocess, os
from pathlib import Path

HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_gaming():
    print("\n  ── Steam + Gaming Tools ──")
    pacman_pkgs = [
        "steam", "lutris", "gamemode", "lib32-gamemode",
        "mangohud", "lib32-mangohud", "gamescope",
        "wine-staging", "winetricks",
        "lib32-gnutls", "lib32-libpulse", "lib32-alsa-plugins",
        "lib32-mesa", "lib32-vulkan-icd-loader",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pacman_pkgs)}", check=False)

    aur_pkgs = [
        "bottles", "heroic-games-launcher-bin",
        "proton-ge-custom-bin",
    ]
    run(f"paru -S --noconfirm --needed {' '.join(aur_pkgs)}", check=False)
    print("  ✓ Gaming tools installés")

def install_discord():
    print("\n  ── Discord (Flatpak Wayland) ──")
    run("flatpak install -y flathub com.discordapp.Discord", check=False)
    print("  ✓ Discord installé")

def configure_gamemode():
    print("\n  ── Configuration GameMode ──")
    gamemode_conf = Path(HOME / ".config/gamemode.ini")
    gamemode_conf.parent.mkdir(parents=True, exist_ok=True)
    conf = """[general]
renice=10
desiredgov=performance
igpu_desiredgov=powersave
defaultgov=powersave
softrealtime=auto
inhibit_screensaver=1

[gpu]
apply_gpu_optimisations=accept-responsibility
gpu_device=0
amd_performance_level=high

[cpu]
park_cores=no
pin_cores=yes

[filter]
whitelist=
blacklist=
"""
    gamemode_conf.write_text(conf)
    # Ajouter l'utilisateur au groupe gamemode
    run(f"sudo usermod -aG gamemode {os.environ.get('HYPERWORLD_USER', 'rayane')}", check=False)
    print("  ✓ GameMode configuré")

if __name__ == "__main__":
    print("\n  ═══ MODULE 06 : APPLICATIONS GAMING ═══\n")
    install_gaming()
    install_discord()
    configure_gamemode()
    print("\n  ✓ Applications Gaming installées !")
