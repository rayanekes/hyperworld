#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 03 — Audio PipeWire + Réseau + Bluetooth
"""
import subprocess, os
from pathlib import Path

HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def setup_audio():
    print("\n  ── PipeWire Audio ──")
    pkgs = ["pipewire", "pipewire-alsa", "pipewire-jack",
            "pipewire-pulse", "wireplumber", "pavucontrol",
            "lib32-pipewire", "playerctl"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}")
    # Activer en mode user (PipeWire tourne par session)
    run("systemctl --user enable pipewire pipewire-pulse wireplumber", check=False)
    print("  ✓ PipeWire configuré")

def setup_network():
    print("\n  ── NetworkManager + iwd ──")
    pkgs = ["networkmanager", "network-manager-applet", "iwd",
            "wireless_tools", "net-tools", "nss-mdns", "firewalld"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}")
    run("sudo systemctl enable NetworkManager firewalld", check=False)
    # Configurer iwd comme backend wifi pour NetworkManager
    nm_conf = Path("/etc/NetworkManager/conf.d/wifi-backend.conf")
    nm_conf.parent.mkdir(parents=True, exist_ok=True)
    nm_conf.write_text("[device]\nwifi.backend=iwd\n")
    print("  ✓ NetworkManager + iwd configurés")

def setup_bluetooth():
    print("\n  ── Bluetooth ──")
    pkgs = ["bluez", "bluez-utils", "blueman"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}")
    run("sudo systemctl enable bluetooth", check=False)
    # Auto-power on bluetooth
    bt_conf = Path("/etc/bluetooth/main.conf")
    if bt_conf.exists():
        content = bt_conf.read_text()
        if "AutoEnable" not in content:
            content += "\n[Policy]\nAutoEnable=true\n"
            tmp = Path("/tmp/bluetooth-main.conf")
            tmp.write_text(content)
            run("sudo mv /tmp/bluetooth-main.conf /etc/bluetooth/main.conf")
    print("  ✓ Bluetooth configuré (auto-enable)")

if __name__ == "__main__":
    print("\n  ═══ MODULE 03 : AUDIO + RÉSEAU + BLUETOOTH ═══\n")
    setup_audio()
    setup_network()
    setup_bluetooth()
    print("\n  ✓ Audio + Réseau + Bluetooth configurés !")
