#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 07 — Applications Cybersécurité
Réseau, Reverse Engineering, Exploitation, OSINT
"""
import subprocess, os
from pathlib import Path
# NOTE P2-3 : packages/cybersec.txt est la liste de référence documentaire.
# Les listes ci-dessous sont les paquets réellement installés (peuvent différer).
# Mise à jour manuelle si tu ajoutes des outils : édite AUSSI packages/cybersec.txt.


HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_network_tools():
    print("\n  ── Outils Réseau ──")
    pkgs = [
        "wireshark-qt", "tshark", "nmap", "aircrack-ng",
        "tcpdump", "masscan", "netdiscover", "arp-scan",
        "openbsd-netcat", "socat", "traceroute",
        "whois", "bind", "net-tools", "ettercap",
        "nethogs", "iftop", "nload",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    # Ajouter user au groupe wireshark
    run(f"sudo usermod -aG wireshark {USER}", check=False)

def install_reverse_engineering():
    print("\n  ── Reverse Engineering ──")
    pacman_pkgs = ["gdb", "radare2", "binwalk", "ltrace", "strace", "xxd"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pacman_pkgs)}", check=False)
    # AUR
    run("paru -S --noconfirm --needed ghidra cutter pwndbg", check=False)

def install_cracking():
    print("\n  ── Password Cracking ──")
    pkgs = ["hydra", "john", "hashcat", "crunch"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)

def install_web_tools():
    print("\n  ── Web & Exploitation ──")
    pkgs = ["sqlmap", "nikto", "gobuster", "proxychains-ng"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    run("paru -S --noconfirm --needed burpsuite exploitdb", check=False)
    # Metasploit
    run("paru -S --noconfirm --needed metasploit", check=False)

def install_anonymity():
    print("\n  ── Anonymat & Tor ──")
    run("sudo pacman -S --noconfirm --needed tor torsocks", check=False)
    run("sudo systemctl enable tor", check=False)
    run("paru -S --noconfirm --needed tor-browser", check=False)

def install_python_tools():
    print("\n  ── Python Security Tools ──")
    # PEP 668 : pas de pip global sur Arch — utiliser pacman quand disponible
    pacman_pkgs = ["python-requests", "python-beautifulsoup4", "python-scapy"]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pacman_pkgs)}", check=False)
    # impacket et pwntools non dispo dans les repos officiels → venv isolé
    venv_dir = HOME / ".axiom" / "cybersec-venv"
    if not venv_dir.exists():
        run(f"python -m venv {venv_dir}", check=False)
    run(f"{venv_dir}/bin/pip install impacket pwntools", check=False)
    print(f"  ✓ Outils Python sécurité installés (venv : {venv_dir})")

if __name__ == "__main__":
    print("\n  ═══ MODULE 07 : CYBERSÉCURITÉ ═══\n")
    install_network_tools()
    install_reverse_engineering()
    install_cracking()
    install_web_tools()
    install_anonymity()
    install_python_tools()
    print("\n  ✓ Outils Cybersécurité installés !")
