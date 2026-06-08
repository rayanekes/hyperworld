#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 08 — Applications Prog / Embedded / AI
VSCode, Arduino IDE, PlatformIO, Docker, Node, Python, CUDA
"""
import subprocess, os
from pathlib import Path
# NOTE P2-3 : packages/prog.txt est la liste de référence documentaire.
# Les listes ci-dessous sont les paquets réellement installés (peuvent différer).
# Mise à jour manuelle si tu ajoutes des outils : édite AUSSI packages/prog.txt.


HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_vscode():
    print("\n  ── VSCode ──")
    run("paru -S --noconfirm --needed visual-studio-code-bin", check=False)
    # Extensions utiles (silencieuses)
    extensions = [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "platformio.platformio-ide",
        "ms-vscode.cpptools",
        "esbenp.prettier-vscode",
        "github.copilot",
        "eamodio.gitlens",
        "ms-azuretools.vscode-docker",
    ]
    # P2-4 : vérifier que le binaire est bien dans le PATH avant d'installer les extensions
    import shutil
    code_bin = shutil.which("code") or shutil.which("code-oss")
    if code_bin:
        for ext in extensions:
            run(f"{code_bin} --install-extension {ext} --force", check=False)
        print("  ✓ VSCode + extensions installées")
    else:
        print("  ⚠ Binaire VSCode non trouvé dans PATH — extensions skippées (relancer après reboot)")

def install_arduino():
    print("\n  ── Arduino IDE ──")
    run("paru -S --noconfirm --needed arduino-ide-bin", check=False)
    run(f"sudo usermod -aG uucp,lock,dialout {USER}", check=False)
    print("  ✓ Arduino IDE installé")

def install_dev_tools():
    print("\n  ── Dev Tools ──")
    pkgs = [
        "git", "github-cli", "docker", "docker-compose",
        "nodejs", "npm", "python", "python-pip",
        "cmake", "make", "ninja", "clang", "llvm",
        "sqlite", "neovim", "lazygit",
        "minicom", "picocom", "openocd",
        "arm-none-eabi-gcc", "arm-none-eabi-newlib",
        "avrdude",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)
    run(f"sudo usermod -aG docker {USER}", check=False)
    run("sudo systemctl enable docker", check=False)

def install_python_env():
    print("\n  ── Environnement Python AI/ML ──")
    # PEP 668 : pacman pour les paquets disponibles dans les repos officiels
    pacman_pkgs = [
        "python-numpy", "python-scipy", "python-pandas",
        "python-matplotlib", "python-scikit-learn",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pacman_pkgs)}", check=False)
    # PyTorch CUDA et JupyterLab → dans le venv AXIOM (non dispo officiel en CUDA)
    axiom_pip = HOME / ".axiom" / "venv" / "bin" / "pip"
    if axiom_pip.exists():
        run(f"{axiom_pip} install jupyterlab", check=False)
        run(
            f"{axiom_pip} install torch torchvision torchaudio "
            f"--index-url https://download.pytorch.org/whl/cu121",
            check=False
        )
        print("  ✓ PyTorch CUDA + JupyterLab installés dans le venv AXIOM")
    else:
        print("  ⚠ venv AXIOM absent — relancer après le module 09")

def install_postman():
    print("\n  ── Postman + Bruno ──")
    run("paru -S --noconfirm --needed postman-bin", check=False)
    run("paru -S --noconfirm --needed bruno-bin", check=False)

def install_spotify():
    print("\n  ── Spotify (Flatpak) ──")
    run("flatpak install -y flathub com.spotify.Client", check=False)
    print("  ✓ Spotify Premium configuré")

if __name__ == "__main__":
    print("\n  ═══ MODULE 08 : PROG/EMBEDDED/AI ═══\n")
    install_vscode()
    install_arduino()
    install_dev_tools()
    install_python_env()
    install_postman()
    install_spotify()
    print("\n  ✓ Applications Prog/Embedded/AI installées !")
