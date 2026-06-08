#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 10 — Déploiement de tous les dotfiles
Place chaque fichier de dotfiles/ exactement au bon endroit.
Crée des symlinks pour faciliter les mises à jour futures.
"""
import subprocess, os, shutil
from pathlib import Path

REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
HOME      = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
CONFIG    = HOME / ".config"

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def symlink(src: Path, dst: Path):
    """Crée un symlink dst → src. Remplace si existant (fichier, symlink ou dossier)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            # Dossier réel (ex: ~/.config/kitty/ créé manuellement) — suppression sécurisée
            shutil.rmtree(dst)
        else:
            dst.unlink()
    dst.symlink_to(src)
    print(f"  ✓  {dst} → {src}")

def deploy_hyprland():
    print("\n  ── Hyprland configs ──")
    src_dir = REPO_ROOT / "dotfiles" / "hyprland"
    dst_dir = CONFIG / "hypr"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src_dir)
                symlink(f, dst_dir / rel)

def deploy_waybar():
    print("\n  ── Waybar configs ──")
    src_dir = REPO_ROOT / "dotfiles" / "waybar"
    dst_dir = CONFIG / "waybar"
    dst_dir.mkdir(parents=True, exist_ok=True)
    # On symlinke le dossier world actif au démarrage (prog par défaut)
    for world in ["gaming", "cybersec", "prog"]:
        src = src_dir / world
        dst = dst_dir / world
        if src.exists():
            if dst.exists() or dst.is_symlink():
                if dst.is_symlink(): dst.unlink()
                else: shutil.rmtree(dst)
            dst.symlink_to(src)
            print(f"  ✓  waybar/{world}")
    # Config active = prog par défaut
    active_src = src_dir / "prog" / "config.jsonc"
    active_style = src_dir / "prog" / "style.css"
    if active_src.exists():
        symlink(active_src, dst_dir / "config.jsonc")
    if active_style.exists():
        symlink(active_style, dst_dir / "style.css")

def deploy_kitty():
    print("\n  ── Kitty configs ──")
    src_dir = REPO_ROOT / "dotfiles" / "kitty"
    dst_dir = CONFIG / "kitty"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for f in src_dir.glob("*.conf") if src_dir.exists() else []:
        symlink(f, dst_dir / f.name)
    # Config active = prog par défaut
    prog_conf = src_dir / "prog.conf"
    if prog_conf.exists():
        symlink(prog_conf, dst_dir / "kitty.conf")

def deploy_rofi():
    print("\n  ── Rofi configs ──")
    src_dir = REPO_ROOT / "dotfiles" / "rofi"
    dst_dir = CONFIG / "rofi"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.iterdir():
            if f.is_file():
                symlink(f, dst_dir / f.name)

def deploy_swaync():
    print("\n  ── SwayNC config ──")
    src_dir = REPO_ROOT / "dotfiles" / "swaync"
    dst_dir = CONFIG / "swaync"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.iterdir():
            if f.is_file():
                symlink(f, dst_dir / f.name)

def deploy_scripts():
    print("\n  ── Scripts runtime ──")
    src_dir = REPO_ROOT / "scripts"
    dst_dir = HOME / ".local" / "bin"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.glob("*.sh"):
            symlink(f, dst_dir / f.name)
            run(f"chmod +x {f}")

def deploy_axiom():
    print("\n  ── AXIOM daemon + configs ──")
    src_dir = REPO_ROOT / "dotfiles" / "axiom"
    dst_dir = HOME / ".axiom"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.iterdir():
            if f.is_file():
                symlink(f, dst_dir / f.name)

def configure_path():
    print("\n  ── Ajout ~/.local/bin au PATH ──")
    zshrc = HOME / ".zshrc"
    bashrc = HOME / ".bashrc"
    path_line = '\nexport PATH="$HOME/.local/bin:$PATH"\n'
    for rc in [zshrc, bashrc]:
        if rc.exists():
            content = rc.read_text()
            if ".local/bin" not in content:
                rc.write_text(content + path_line)
                print(f"  ✓ PATH mis à jour dans {rc.name}")

def configure_starship():
    print("\n  ── Starship prompt ──")
    src = REPO_ROOT / "dotfiles" / "starship.toml"
    dst = CONFIG / "starship.toml"
    if src.exists():
        symlink(src, dst)
    else:
        # Config starship minimale HYPERWORLD
        dst.write_text("""# HYPERWORLD — Starship Prompt
format = """
"$directory$git_branch$git_status$python$nodejs$rust$cmd_duration$line_break$character"
"""
[character]
success_symbol = "[⟩](bold cyan)"
error_symbol = "[⟩](bold red)"

[directory]
style = "bold cyan"
truncation_length = 3

[git_branch]
symbol = " "
style = "bold magenta"
""")
        print("  ✓ Starship configuré")

def deploy_zshrc():
    print("\n  ── .zshrc HYPERWORLD ──")
    src = REPO_ROOT / "dotfiles" / "zshrc"
    dst = HOME / ".zshrc"
    if src.exists():
        # Backup de l'ancien .zshrc si existant
        if dst.exists() and not dst.is_symlink():
            backup = HOME / ".zshrc.backup"
            dst.rename(backup)
            print(f"  ✓ Ancien .zshrc sauvegardé → {backup}")
        symlink(src, dst)
        print("  ✓ .zshrc HYPERWORLD déployé")

def deploy_wallpapers():
    print("\n  ── Wallpapers (téléchargement) ──")
    wallpaper_script = REPO_ROOT / "scripts" / "get-wallpapers.sh"
    wallpaper_dir    = REPO_ROOT / "dotfiles" / "wallpapers"
    wallpaper_dir.mkdir(parents=True, exist_ok=True)
    if wallpaper_script.exists():
        import subprocess
        run(f"bash {wallpaper_script}", check=False)
    else:
        print("  ⚠ get-wallpapers.sh introuvable")

def deploy_hyprlock():
    """Lien symlink hyprlock.conf → ~/.config/hypr/hyprlock.conf"""
    src = REPO_ROOT / "dotfiles" / "hyprland" / "hyprlock.conf"
    dst = CONFIG / "hypr" / "hyprlock.conf"
    if src.exists():
        symlink(src, dst)

def deploy_hypridle():
    """Lien symlink hypridle.conf → ~/.config/hypr/hypridle.conf"""
    src = REPO_ROOT / "dotfiles" / "hyprland" / "hypridle.conf"
    dst = CONFIG / "hypr" / "hypridle.conf"
    if src.exists():
        symlink(src, dst)

def deploy_hyperboard():
    """Déploie HyperBoard (dashboard Super key) dans ~/.config/hypr/hyperboard/"""
    print("\n  ── HyperBoard dashboard ──")
    src_dir = REPO_ROOT / "dotfiles" / "hyperboard"
    dst_dir = CONFIG / "hypr" / "hyperboard"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.iterdir():
            if f.is_file():
                symlink(f, dst_dir / f.name)
        print("  ✓ HyperBoard déployé → ~/.config/hypr/hyperboard/")
    else:
        print("  ⚠ Dossier hyperboard introuvable")

def deploy_swappy():
    """Déploie la config swappy pour les screenshots"""
    print("\n  ── swappy config ──")
    src = REPO_ROOT / "dotfiles" / "swappy" / "config"
    dst_dir = CONFIG / "swappy"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "config"
    if src.exists():
        symlink(src, dst)
        # Créer le dossier de screenshots
        screenshots_dir = HOME / "Pictures" / "Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ swappy configuré → {dst}")
        print(f"  ✓ Dossier screenshots : {screenshots_dir}")
    else:
        print("  ⚠ config swappy introuvable")

if __name__ == "__main__":
    print("\n  ═══ MODULE 10 : DÉPLOIEMENT DOTFILES ═══\n")
    deploy_hyprland()
    deploy_waybar()
    deploy_kitty()
    deploy_rofi()
    deploy_swaync()
    deploy_scripts()
    deploy_axiom()
    deploy_zshrc()
    deploy_hyprlock()
    deploy_hypridle()
    deploy_hyperboard()
    deploy_swappy()
    configure_path()
    configure_starship()
    deploy_wallpapers()
    print("\n  ✓ Tous les dotfiles déployés via symlinks !")

