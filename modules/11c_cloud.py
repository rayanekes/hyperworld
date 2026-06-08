#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 11c — Intégration Cloud (Google Drive + Google Photos)

Installe rclone + zenity + configure les services systemd
pour la synchronisation automatique.
"""
import subprocess, os
from pathlib import Path

HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))
REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_rclone():
    """Installe rclone + dépendances"""
    print("\n  ── rclone + dépendances cloud ──")
    pkgs = [
        "rclone",       # backend universel cloud
        "zenity",       # dialogue fichier GUI (GTK natif Wayland)
        "fuse3",        # monter Drive comme filesystem
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    print("  ✓ rclone installé")

def deploy_gdrive_script():
    """Déploie gdrive.sh dans ~/.local/bin/"""
    print("\n  ── Script gdrive.sh ──")
    import shutil
    src = REPO_ROOT / "scripts" / "gdrive.sh"
    dst = HOME / ".local" / "bin" / "gdrive.sh"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
        dst.chmod(0o755)
        print(f"  ✓ gdrive.sh → {dst}")

def create_sync_service():
    """Crée le service systemd user pour l'auto-sync"""
    print("\n  ── Service systemd gdrive-sync ──")

    service = """[Unit]
Description=HYPERWORLD — Sync Google Drive auto
After=network-online.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/gdrive.sh sync
StandardOutput=append:%h/.local/share/hyperworld/gdrive-sync.log
StandardError=append:%h/.local/share/hyperworld/gdrive-sync.log
"""

    timer = """[Unit]
Description=HYPERWORLD — Auto-sync Google Drive toutes les 30 min
Requires=gdrive-sync.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
"""

    # Service photos (toutes les heures)
    photos_service = """[Unit]
Description=HYPERWORLD — Backup Google Photos auto
After=network-online.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/gdrive.sh photos
StandardOutput=append:%h/.local/share/hyperworld/gdrive-sync.log
"""

    photos_timer = """[Unit]
Description=HYPERWORLD — Backup Google Photos toutes les heures

[Timer]
OnBootSec=10min
OnUnitActiveSec=60min
Persistent=true

[Install]
WantedBy=timers.target
"""

    svc_dir = HOME / ".config" / "systemd" / "user"
    svc_dir.mkdir(parents=True, exist_ok=True)

    (svc_dir / "gdrive-sync.service").write_text(service)
    (svc_dir / "gdrive-sync.timer").write_text(timer)
    (svc_dir / "gphotos-backup.service").write_text(photos_service)
    (svc_dir / "gphotos-backup.timer").write_text(photos_timer)

    run("systemctl --user daemon-reload", check=False)
    # NE PAS activer automatiquement — l'user le fait via gdrive.sh
    print("  ✓ Services systemd créés (activer via Super+G → 'Activer sync auto')")

def create_rclone_config_helper():
    """Crée un script d'aide à la configuration initiale de rclone"""
    print("\n  ── Script de configuration rclone ──")

    helper = """#!/usr/bin/env bash
# HYPERWORLD — Configuration initiale rclone
# Lance ce script UNE FOIS pour connecter Google Drive et Google Photos

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     Configuration Google Drive + Google Photos       ║"
echo "║                 pour HYPERWORLD                      ║"
╚══════════════════════════════════════════════════════╝"
echo ""
echo "Ce script va configurer 2 remotes rclone :"
echo "  1) gdrive   → Google Drive (fichiers)"
echo "  2) gphotos  → Google Photos (photos/vidéos)"
echo ""
echo "Un navigateur va s'ouvrir pour l'autorisation Google."
echo ""
read -p "Appuie sur Entrée pour commencer..."

echo ""
echo "═══ ÉTAPE 1 : Google Drive ═══"
echo "Dans rclone config, fais :"
echo "  n (new remote)"
echo "  Name: gdrive"
echo "  Storage: 18 (Google Drive)"
echo "  Client ID: (laisser vide)"
echo "  Client Secret: (laisser vide)"
echo "  Scope: 1 (full access)"
echo "  Service Account: (laisser vide)"
echo "  Advanced: n"
echo "  Auto config: y  ← le navigateur va s'ouvrir"
echo "  Team Drive: n"
echo "  OK: y"
echo ""
read -p "Prêt ? Appuie sur Entrée..."
rclone config

echo ""
echo "═══ ÉTAPE 2 : Google Photos ═══"
echo "Dans rclone config, fais :"
echo "  n (new remote)"
echo "  Name: gphotos"
echo "  Storage: 7 (Google Photos)"
echo "  Client ID: (laisser vide)"
echo "  Client Secret: (laisser vide)"
echo "  read only: false"
echo "  Auto config: y"
echo ""
read -p "Prêt ? Appuie sur Entrée..."
rclone config

echo ""
echo "✓ Configuration terminée !"
echo ""
echo "Remotes configurés :"
rclone listremotes
echo ""
echo "Test Google Drive :"
rclone ls gdrive: --max-depth 1 2>/dev/null | head -5
echo ""
echo "Test Google Photos :"
rclone ls gphotos:album --max-depth 1 2>/dev/null | head -5
echo ""
echo "Maintenant utilise Super+G pour accéder à Google Drive !"
read -p "Appuie sur Entrée pour fermer..."
"""

    dst = HOME / ".local" / "bin" / "setup-gdrive.sh"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(helper)
    dst.chmod(0o755)
    print(f"  ✓ setup-gdrive.sh → {dst}")
    print("    Lance 'setup-gdrive.sh' une fois pour connecter ton compte Google")

def update_hypersettings_zshrc():
    """Ajoute alias gdrive dans .zshrc"""
    print("\n  ── Alias gdrive dans .zshrc ──")
    zshrc = REPO_ROOT / "dotfiles" / "zshrc"
    if zshrc.exists():
        content = zshrc.read_text(encoding="utf-8")
        alias_block = """
# ── Google Drive / Cloud ──────────────────────────────
alias gdrive='$HOME/.local/bin/gdrive.sh'
alias gd-sync='$HOME/.local/bin/gdrive.sh sync'
alias gd-status='$HOME/.local/bin/gdrive.sh status'
alias gd-setup='$HOME/.local/bin/setup-gdrive.sh'
"""
        if "Google Drive" not in content:
            content += alias_block
            zshrc.write_text(content, encoding="utf-8")
            print("  ✓ Alias Google Drive ajoutés dans .zshrc")
        else:
            print("  ✓ Alias déjà présents")

if __name__ == "__main__":
    print("\n  ═══ MODULE 11c : INTÉGRATION CLOUD GOOGLE ═══\n")
    install_rclone()
    deploy_gdrive_script()
    create_sync_service()
    create_rclone_config_helper()
    update_hypersettings_zshrc()
    print("""
  ✓ Intégration Google Drive prête !

  ╔══════════════════════════════════════════════════════╗
  ║  PREMIÈRE UTILISATION :                             ║
  ║                                                     ║
  ║  1) Lance une fois :  setup-gdrive.sh               ║
  ║     (connecte ton compte Google via navigateur)     ║
  ║                                                     ║
  ║  2) Ensuite : Super+G pour tout contrôler           ║
  ╚══════════════════════════════════════════════════════╝

  Raccourcis terminal :
    gdrive        → menu interactif
    gd-sync       → sync immédiate
    gd-status     → état de la connexion
""")
