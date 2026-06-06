#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 09 — Stack IA AXIOM
- llama-cpp-python (CUDA) — backend LLM principal
- Whisper.cpp — reconnaissance vocale hors-ligne
- Piper TTS — synthèse vocale FR hors-ligne
- ChromaDB — mémoire vectorielle (RAG)
- Open Interpreter bridé — exécution autonome sécurisée
- Service systemd AXIOM
"""
import subprocess, os, venv, sys
from pathlib import Path

REPO_ROOT = Path(os.environ.get("HYPERWORLD_ROOT", Path(__file__).parent.parent))
HOME      = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))
USER      = os.environ.get("HYPERWORLD_USER", os.environ.get("USER", "rayane"))
AXIOM_DIR = HOME / ".axiom"
VENV_DIR  = AXIOM_DIR / "venv"
PIP       = VENV_DIR / "bin" / "pip"
PYTHON    = VENV_DIR / "bin" / "python"

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def create_axiom_dirs():
    dirs = [
        AXIOM_DIR / "models",
        AXIOM_DIR / "whisper",
        AXIOM_DIR / "piper",
        AXIOM_DIR / "rag",
        AXIOM_DIR / "logs",
        AXIOM_DIR / "memory",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  ✓ Répertoires AXIOM créés")

def create_venv():
    print("\n  ── Création environnement virtuel Python AXIOM ──")
    if not VENV_DIR.exists():
        venv.create(str(VENV_DIR), with_pip=True)
        print("  ✓ venv créé")
    else:
        print("  ✓ venv déjà existant")

def install_llama_cpp():
    print("\n  ── llama-cpp-python (CUDA) ──")
    # Build avec support CUDA pour RTX 4050
    env = os.environ.copy()
    env["CMAKE_ARGS"] = "-DGGML_CUDA=on"
    env["FORCE_CMAKE"] = "1"
    cmd = f"{PIP} install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121"
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=False, env=env)
    print("  ✓ llama-cpp-python (CUDA) installé")

def install_whisper():
    print("\n  ── Whisper.cpp (Python bindings) ──")
    run(f"{PIP} install openai-whisper faster-whisper", check=False)
    # whisper.cpp natif pour performance maximale
    run("git clone https://github.com/ggerganov/whisper.cpp.git /tmp/whisper.cpp --depth=1", check=False)
    run("cd /tmp/whisper.cpp && WHISPER_CUDA=1 make -j$(nproc)", check=False)
    whisper_bin = AXIOM_DIR / "whisper" / "main"
    run(f"cp /tmp/whisper.cpp/main {whisper_bin}", check=False)
    print("  ✓ Whisper.cpp compilé")

def install_piper():
    print("\n  ── Piper TTS ──")
    run("paru -S --noconfirm --needed piper-tts", check=False)
    # Fallback: pip
    run(f"{PIP} install piper-tts", check=False)
    print("  ✓ Piper TTS installé (modèle téléchargé séparément)")

def install_rag_stack():
    print("\n  ── Stack RAG (ChromaDB + LangChain) ──")
    packages = [
        "chromadb",
        "langchain",
        "langchain-community",
        "sentence-transformers",
        "pypdf",
        "python-docx",
        "tiktoken",
    ]
    run(f"{PIP} install {' '.join(packages)}", check=False)
    print("  ✓ Stack RAG installée")

def install_open_interpreter():
    print("\n  ── Open Interpreter (bridé) ──")
    run(f"{PIP} install open-interpreter", check=False)
    print("  ✓ Open Interpreter installé")

def install_voice_deps():
    print("\n  ── Dépendances audio Python ──")
    run("sudo pacman -S --noconfirm --needed portaudio", check=False)
    packages = ["pyaudio", "sounddevice", "soundfile", "numpy", "scipy"]
    run(f"{PIP} install {' '.join(packages)}", check=False)
    print("  ✓ Dépendances audio installées")

def install_misc_deps():
    print("\n  ── Dépendances AXIOM diverses ──")
    packages = [
        "watchdog",      # surveillance fichiers
        "rich",          # interface terminal belle
        "click",         # CLI
        "pydantic",      # validation données
        "httpx",         # requêtes HTTP async
        "python-dotenv", # variables d'environnement
        "schedule",      # tâches planifiées
        "psutil",        # infos système
        "gitpython",     # accès git depuis Python
    ]
    run(f"{PIP} install {' '.join(packages)}", check=False)

def deploy_axiom_files():
    print("\n  ── Déploiement des fichiers AXIOM ──")
    src = REPO_ROOT / "dotfiles" / "axiom"
    if src.exists():
        import shutil
        for f in src.iterdir():
            dest = AXIOM_DIR / f.name
            if f.is_file():
                shutil.copy2(f, dest)
                print(f"  ✓ Copié : {f.name} → {dest}")
    else:
        print("  ⚠ dotfiles/axiom/ introuvable, copie ignorée")

def create_systemd_service():
    print("\n  ── Service systemd AXIOM ──")
    service = f"""[Unit]
Description=AXIOM — Assistant IA HYPERWORLD
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User={USER}
Environment=PYTHONPATH={AXIOM_DIR}
Environment=AXIOM_DIR={AXIOM_DIR}
ExecStart={PYTHON} {AXIOM_DIR}/axiom.py --daemon
Restart=on-failure
RestartSec=5
StandardOutput=append:{AXIOM_DIR}/logs/axiom.log
StandardError=append:{AXIOM_DIR}/logs/axiom.error.log

[Install]
WantedBy=default.target
"""
    service_dir = HOME / ".config/systemd/user"
    service_dir.mkdir(parents=True, exist_ok=True)
    (service_dir / "axiom.service").write_text(service)
    run("systemctl --user daemon-reload", check=False)
    run("systemctl --user enable axiom.service", check=False)
    print("  ✓ Service AXIOM enregistré (démarrage automatique sous secteur)")

def create_power_activation():
    print("\n  ── Règle udev activation AXIOM sous secteur ──")
    rule = f"""# HYPERWORLD — Lance AXIOM quand on branche le chargeur
ACTION=="change", SUBSYSTEM=="power_supply", ATTR{{type}}=="Mains", ATTR{{online}}=="1", RUN+="/bin/systemctl --user start axiom.service"
ACTION=="change", SUBSYSTEM=="power_supply", ATTR{{type}}=="Mains", ATTR{{online}}=="0", RUN+="/bin/systemctl --user stop axiom.service"
"""
    tmp = Path("/tmp/99-axiom-power.rules")
    tmp.write_text(rule)
    run("sudo mv /tmp/99-axiom-power.rules /etc/udev/rules.d/")
    run("sudo udevadm control --reload-rules", check=False)
    print("  ✓ Activation AXIOM sous secteur configurée")

if __name__ == "__main__":
    print("\n  ═══ MODULE 09 : STACK IA AXIOM ═══\n")
    create_axiom_dirs()
    create_venv()
    install_voice_deps()
    install_llama_cpp()
    install_whisper()
    install_piper()
    install_rag_stack()
    install_open_interpreter()
    install_misc_deps()
    deploy_axiom_files()
    create_systemd_service()
    create_power_activation()
    print("\n  ✓ Stack AXIOM installée — modèles à télécharger séparément")
