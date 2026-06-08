#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 11b — Centre de Contrôle HYPERWORLD
Installe les outils de gestion d'applications et de paramètres système.

Outils installés :
  Store graphique  : Bauh (AUR+Flatpak+AppImage+Snap unifié)
  Flatpak apps     : Flatseal, Warehouse, Mission Center, EasyEffects
  Système          : Stacer, Timeshift, Firejail, ncdu, paccache
  Interface        : nwg-look, wdisplays, pavucontrol, blueman
  Réseau           : nm-connection-editor
  Sécurité         : KeePassXC
"""
import subprocess, os, shutil
from pathlib import Path

HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_store_gui():
    """Bauh — store graphique unifié (AUR + Flatpak + AppImage + Snap)"""
    print("\n  ── Bauh Store (AUR + Flatpak + AppImage) ──")
    run("paru -S --noconfirm --needed bauh", check=False)
    # Dépendances Bauh pour tous les backends
    run("sudo pacman -S --noconfirm --needed python-requests python-pyqt5 python-pip", check=False)
    print("  ✓ Bauh Store installé")

def install_flatpak_apps():
    """Applications Flatpak premium de gestion"""
    print("\n  ── Flatpak Apps (gestion + monitoring) ──")
    apps = [
        ("Flatseal",        "com.github.tchx84.Flatseal"),   # Permissions style Android
        ("Warehouse",       "io.github.flattool.Warehouse"),  # Gestionnaire Flatpak
        ("Mission Center",  "io.missioncenter.MissionCenter"), # Moniteur ressources par app
        ("EasyEffects",     "com.github.wwmm.easyeffects"),  # Égaliseur audio
    ]
    for name, app_id in apps:
        print(f"  ↓ {name}...")
        run(f"flatpak install -y flathub {app_id}", check=False)
    print("  ✓ Applications Flatpak de gestion installées")

def install_system_tools():
    """Outils système : nettoyage, snapshots, monitoring"""
    print("\n  ── Outils Système & Maintenance ──")

    # Outils pacman
    pacman_pkgs = [
        # Nettoyage
        "pacman-contrib",      # paccache (nettoyage cache)
        "ncdu",                # analyseur disque NCurses
        # Réseau
        "networkmanager-applet",
        "nm-connection-editor" if shutil.which("nm-connection-editor") is None else None,
        # Audio
        "pavucontrol",         # Contrôle volume PipeWire/PulseAudio
        # Bluetooth
        "blueman",             # Gestionnaire Bluetooth GUI
        # Apparence
        "nwg-look",            # Paramètres GTK Wayland
        "wdisplays",           # Gestionnaire moniteurs Wayland
        # Sécurité sandboxing
        "firejail",            # Sandbox applications
        "apparmor",            # Contrôle accès mandataire
        # Snapshots
        "timeshift",           # Snapshots système BTRFS/rsync
        # Divers
        "keepassxc",           # Gestionnaire mots de passe
    ]
    pkgs = [p for p in pacman_pkgs if p]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)

    # Stacer (AUR) — nettoyeur système complet
    run("paru -S --noconfirm --needed stacer", check=False)

    print("  ✓ Outils système installés")

def configure_timeshift():
    """Configure Timeshift pour snapshots auto BTRFS"""
    print("\n  ── Configuration Timeshift ──")
    # Activer cronie pour les snapshots automatiques
    run("sudo pacman -S --noconfirm --needed cronie", check=False)
    run("sudo systemctl enable cronie", check=False)
    print("  ✓ Timeshift prêt — lance 'pkexec timeshift-gtk' pour configurer")

def configure_firejail():
    """Active le sandboxing Firejail pour les apps risquées"""
    print("\n  ── Configuration Firejail ──")
    run("sudo firecfg", check=False)
    print("  ✓ Firejail activé — les apps sensibles sont sandboxées")

def deploy_hypersettings_script():
    """Déploie le script HyperSettings dans ~/.local/bin/"""
    print("\n  ── Script HyperSettings ──")
    from pathlib import Path
    import shutil

    REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
    src = REPO_ROOT / "scripts" / "hypersettings.sh"
    dst = HOME / ".local" / "bin" / "hypersettings.sh"
    dst.parent.mkdir(parents=True, exist_ok=True)

    if src.exists():
        shutil.copy2(src, dst)
        dst.chmod(0o755)
        print(f"  ✓ hypersettings.sh → {dst}")
    else:
        print("  ⚠ hypersettings.sh introuvable")

    # Thème Rofi
    rofi_src = REPO_ROOT / "dotfiles" / "rofi" / "hypersettings.rasi"
    rofi_dst = HOME / ".config" / "rofi" / "hypersettings.rasi"
    rofi_dst.parent.mkdir(parents=True, exist_ok=True)
    if rofi_src.exists():
        shutil.copy2(rofi_src, rofi_dst)
        print(f"  ✓ hypersettings.rasi → {rofi_dst}")

def configure_apparmor():
    """Active AppArmor au boot"""
    print("\n  ── AppArmor ──")
    run("sudo systemctl enable apparmor", check=False)
    # Ajouter apparmor aux paramètres kernel si GRUB
    grub = Path("/etc/default/grub")
    if grub.exists():
        content = grub.read_text()
        if "apparmor=1" not in content:
            import re
            content = re.sub(
                r'(GRUB_CMDLINE_LINUX_DEFAULT="[^"]*?)(")',
                lambda m: m.group(1) + " apparmor=1 lsm=landlock,lockdown,yama,integrity,apparmor,bpf" + m.group(2),
                content
            )
            tmp = Path("/tmp/grub-apparmor.conf")
            tmp.write_text(content)
            run("sudo mv /tmp/grub-apparmor.conf /etc/default/grub")
            run("sudo grub-mkconfig -o /boot/grub/grub.cfg", check=False)
    print("  ✓ AppArmor activé")

if __name__ == "__main__":
    print("\n  ═══ MODULE 11b : CENTRE DE CONTRÔLE ═══\n")
    install_store_gui()
    install_flatpak_apps()
    install_system_tools()
    configure_timeshift()
    configure_firejail()
    configure_apparmor()
    deploy_hypersettings_script()
    print("""
  ✓ Centre de contrôle HYPERWORLD installé !

  Accès via keybind : Super + S
  Ou lance : hypersettings.sh

  Outils disponibles :
    🛍️  Bauh           → store AUR + Flatpak + AppImage
    🔐  Flatseal       → permissions Flatpak (style Android)
    📦  Warehouse      → gestion stockage Flatpak
    ⚡  Mission Center → ressources par application
    🧹  Stacer         → nettoyage + services + démarrage
    💾  Timeshift      → snapshots système
    🎨  nwg-look       → apparence GTK
    🔵  Blueman        → Bluetooth
    🔊  pavucontrol    → audio
    📡  nm-editor      → réseau & VPN
""")
