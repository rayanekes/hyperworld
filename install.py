#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║        HYPERWORLD — Master Orchestrator v1.0             ║
║   Arch Linux + Hyprland + AXIOM — Setup Autonome        ║
║                                                          ║
║  Usage: python install.py                                ║
╚══════════════════════════════════════════════════════════╝
"""

import json, os, sys, subprocess, time, logging, importlib.util
from pathlib import Path
from datetime import datetime
from typing import Optional

# ── Constantes ─────────────────────────────────────────────────
REPO_ROOT  = Path(__file__).parent.resolve()
STATE_FILE = REPO_ROOT / "state.json"
LOG_FILE   = REPO_ROOT / "install.log"
MODELS_FILE= REPO_ROOT / "packages" / "models.json"
HOME       = Path.home()
CONFIG     = HOME / ".config"
USER       = os.environ.get("USER", "rayane")

MODULES = [
    ("01_base_arch",      "Base système Arch Linux"),
    ("02_nvidia_drivers", "Pilotes NVIDIA RTX 4050 + Wayland"),
    ("03_audio_network",  "Audio PipeWire + Réseau + Bluetooth"),
    ("04_hyprland_core",  "Hyprland + Stack Wayland complète"),
    ("05_world_system",   "Système Multi-Monde + Scripts"),
    ("06_apps_gaming",    "Applications Monde Gaming"),
    ("07_apps_cybersec",  "Applications Monde Cybersécurité"),
    ("08_apps_prog",      "Applications Monde Prog/Embedded/AI"),
    ("09_ai_stack",       "Stack IA AXIOM (llama-cpp-python)"),
    ("10_dotfiles",       "Déploiement de tous les dotfiles"),
    ("11_finalize",       "Finalisation + services systemd"),
]

C = {
    "r": "\033[0m",   "bold": "\033[1m",
    "red": "\033[91m","green":"\033[92m","yellow":"\033[93m",
    "blue":"\033[94m","mag":  "\033[95m","cyan":  "\033[96m",
}
def c(color, text): return f"{C.get(color,'')}{text}{C['r']}"

# ── Banner ──────────────────────────────────────────────────────
def banner():
    print(c("cyan", """
╔══════════════════════════════════════════════════════════╗
║  ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗               ║
║  ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗              ║
║  ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝              ║
║  ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗              ║
║  ██║  ██║   ██║   ██║     ███████╗██║  ██║               ║
║  ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝  WORLD      ║
║                                                          ║
║      Arch Linux + Hyprland + AXIOM — v1.0               ║
╚══════════════════════════════════════════════════════════╝
"""))

# ── Logging ─────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ]
    )

# ── State Management ────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "1.0",
        "started_at": datetime.now().isoformat(),
        "last_run": None,
        "completed_steps": [],
        "current_module": None,
        "downloads": {},
        "errors": [],
        "completed": False,
    }

def save_state(state: dict):
    state["last_run"] = datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def mark_done(state: dict, step: str):
    if step not in state["completed_steps"]:
        state["completed_steps"].append(step)
    save_state(state)

def is_done(state: dict, step: str) -> bool:
    return step in state["completed_steps"]

# ── Commandes système ───────────────────────────────────────────
def run(cmd: str, check: bool = True, env: dict = None) -> int:
    logging.info(f"CMD: {cmd}")
    e = os.environ.copy()
    if env:
        e.update(env)
    result = subprocess.run(cmd, shell=True, check=check, env=e)
    return result.returncode

def pacman(*packages: str):
    """Installe des paquets via pacman (--needed = skip si déjà installé)"""
    pkgs = " ".join(packages)
    run(f"sudo pacman -S --noconfirm --needed {pkgs}")

def paru(*packages: str):
    """Installe des paquets AUR via paru"""
    pkgs = " ".join(packages)
    run(f"paru -S --noconfirm --needed {pkgs}")

def flatpak(*app_ids: str):
    for app in app_ids:
        run(f"flatpak install -y flathub {app}", check=False)

def systemctl_enable(*services: str):
    for s in services:
        run(f"sudo systemctl enable {s}", check=False)

def systemctl_enable_user(*services: str):
    for s in services:
        run(f"systemctl --user enable {s}", check=False)

# ── Downloader intelligent ──────────────────────────────────────
def download(
    url: str,
    dest_dir: Path,
    name: str,
    state: dict,
    retries: int = 3,
    fallback_url: Optional[str] = None,
) -> bool:
    """
    Télécharge un fichier avec reprise, retry, et fallback navigateur.
    Utilise wget --continue pour reprendre les téléchargements partiels.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(url.split("?")[0]).name
    dest_path = dest_dir / filename
    dl_key = str(dest_path)

    # Déjà téléchargé ?
    if state["downloads"].get(dl_key) == "completed" and dest_path.exists():
        print(c("green", f"  ✓ [CACHE] {name}"))
        return True

    state["downloads"][dl_key] = "in_progress"
    save_state(state)

    for attempt in range(1, retries + 1):
        try:
            print(c("cyan", f"\n  ⬇  [{attempt}/{retries}] {name}"))
            print(c("yellow", f"      → {dest_path}"))
            run(f'wget -c --progress=bar:force:noscroll -O "{dest_path}" "{url}"')
            state["downloads"][dl_key] = "completed"
            save_state(state)
            print(c("green", f"  ✓ Terminé : {name}"))
            return True
        except subprocess.CalledProcessError:
            print(c("red", f"  ✗ Tentative {attempt} échouée"))
            if attempt < retries:
                print(c("yellow", "  ↺ Retry dans 5s..."))
                time.sleep(5)

    # Toutes les tentatives ont échoué
    state["downloads"][dl_key] = "failed"
    state["errors"].append({"step": "download", "name": name, "url": url})
    save_state(state)

    fb = fallback_url or "/".join(url.split("/")[:6])
    print(c("red", f"""
  ╔══════════════════════════════════════════════════════╗
  ║  ⚠  TÉLÉCHARGEMENT ÉCHOUÉ — ACTION MANUELLE        ║
  ╠══════════════════════════════════════════════════════╣
  ║  Fichier  : {name[:48]:<48} ║
  ║  Placer à : {str(dest_path)[:48]:<48} ║
  ╚══════════════════════════════════════════════════════╝"""))
    print(c("yellow", f"\n  → Ouverture : {fb}\n"))
    subprocess.Popen(["firefox", fb], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    input(c("mag", "  [ENTRÉE une fois le fichier téléchargé et placé] "))

    if dest_path.exists():
        state["downloads"][dl_key] = "completed_manual"
        save_state(state)
        print(c("green", "  ✓ Fichier détecté, on continue !"))
        return True

    print(c("red", "  ✗ Fichier toujours manquant — module ignoré"))
    return False

def download_all_models(state: dict):
    """Télécharge tous les modèles AI définis dans models.json"""
    if not MODELS_FILE.exists():
        print(c("red", "  ✗ packages/models.json introuvable"))
        return

    with open(MODELS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(c("mag", "\n  ════ TÉLÉCHARGEMENT DES MODÈLES AI ════\n"))
    for model in data["models"]:
        dest = Path(model["destination"].replace("~", str(HOME)))
        download(
            url=model["url"],
            dest_dir=dest,
            name=model["name"],
            state=state,
            fallback_url=model.get("fallback_url"),
        )

# ── Affichage progression ───────────────────────────────────────
def show_progress(state: dict):
    print(c("bold", "\n  ════ PROGRESSION ════"))
    for mid, desc in MODULES:
        done = is_done(state, mid)
        icon = c("green", "✓") if done else c("yellow", "○")
        line = c("green", desc) if done else c("white", desc)
        print(f"  {icon}  {line}")
    total = len(MODULES)
    done_n = sum(1 for m, _ in MODULES if is_done(state, m))
    pct = int((done_n / total) * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    print(f"\n  [{c('cyan', bar)}] {pct}%  ({done_n}/{total} modules)\n")

# ── Service reprise auto (systemd) ──────────────────────────────
def install_resume_service():
    svc = f"""[Unit]
Description=HyperWorld Resume Installer
After=network-online.target
Wants=network-online.target
ConditionPathExists={REPO_ROOT}/state.json

[Service]
Type=oneshot
User={USER}
WorkingDirectory={REPO_ROOT}
ExecStart=/bin/bash -c 'python3 -c "import json; d=json.load(open(\\"{STATE_FILE}\\")); exit(0 if d.get(\\'completed\\') else 1)" || {sys.executable} {REPO_ROOT}/install.py'
RemainAfterExit=yes
StandardOutput=journal

[Install]
WantedBy=multi-user.target
"""
    svc_path = Path("/tmp/hyperworld-resume.service")
    svc_path.write_text(svc)
    run("sudo mv /tmp/hyperworld-resume.service /etc/systemd/system/")
    run("sudo systemctl daemon-reload")
    run("sudo systemctl enable hyperworld-resume.service")
    print(c("green", "  ✓ Service de reprise automatique activé"))

# ── Exécution d'un module ───────────────────────────────────────
def run_module(module_id: str, description: str, state: dict):
    if is_done(state, module_id):
        print(c("green", f"  ✓ [SKIP] {description}"))
        return

    print(c("cyan", f"\n{'═'*60}"))
    print(c("bold",  f"  ▶  {description.upper()}"))
    print(c("cyan",  f"{'═'*60}\n"))

    state["current_module"] = module_id
    save_state(state)

    module_file = REPO_ROOT / "modules" / f"{module_id}.py"
    if not module_file.exists():
        print(c("red", f"  ✗ Module introuvable : {module_file}"))
        return

    env = {
        "HYPERWORLD_ROOT": str(REPO_ROOT),
        "HYPERWORLD_HOME": str(HOME),
        "HYPERWORLD_USER": USER,
    }
    try:
        run(f"{sys.executable} {module_file}", env=env)
        mark_done(state, module_id)
        print(c("green", f"\n  ✓  TERMINÉ : {description}"))
    except subprocess.CalledProcessError as e:
        msg = f"Module {module_id} échoué : {e}"
        state["errors"].append({"module": module_id, "error": msg})
        save_state(state)
        print(c("red", f"\n  ✗  ERREUR : {msg}"))
        print(c("yellow", "  → Détails dans install.log"))
        choice = input(c("mag", "  Continuer quand même ? [o/N] : ")).strip().lower()
        if choice != "o":
            print(c("red", "  Installation suspendue. Relance install.py pour reprendre."))
            sys.exit(1)

# ── Point d'entrée ──────────────────────────────────────────────
def main():
    banner()
    setup_logging()
    state = load_state()

    if state.get("completed"):
        print(c("green", "\n  ✓ HYPERWORLD est déjà installé !"))
        print(c("cyan", "  Supprime state.json pour réinstaller.\n"))
        sys.exit(0)

    show_progress(state)

    # Service de reprise au boot
    try:
        install_resume_service()
    except Exception as e:
        print(c("yellow", f"  ⚠ Service reprise non installé (non bloquant) : {e}"))

    # Exécution de tous les modules dans l'ordre
    for module_id, description in MODULES:
        run_module(module_id, description, state)

    # Téléchargement des modèles AI
    download_all_models(state)

    # Installation complète
    state["completed"] = True
    state["completed_at"] = datetime.now().isoformat()
    save_state(state)

    print(c("cyan", """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    ✓   HYPERWORLD — INSTALLATION COMPLÈTE !             ║
║                                                          ║
║    → Redémarre : sudo reboot                            ║
║    → Super+F1/F2/F3 : changer de monde                 ║
║    → Super         : vue globale de toutes les apps     ║
║    → Super+A       : invoquer AXIOM                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""))
    reboot = input(c("mag", "  Redémarrer maintenant ? [o/N] : ")).strip().lower()
    if reboot == "o":
        run("sudo reboot")

if __name__ == "__main__":
    main()
