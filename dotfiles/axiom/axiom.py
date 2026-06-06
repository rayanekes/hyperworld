#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║             AXIOM — Assistant IA HYPERWORLD             ║
║   llama-cpp-python + Whisper + Piper + ChromaDB RAG     ║
║                                                          ║
║  Mode daemon : axiom.py --daemon                        ║
║  Mode interactif : axiom.py --interactive               ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, json, time, signal, queue, threading, subprocess
from pathlib import Path
from datetime import datetime

# ── Chemins ─────────────────────────────────────────────────
AXIOM_DIR  = Path(os.environ.get("AXIOM_DIR", Path.home() / ".axiom"))
MODEL_PATH = AXIOM_DIR / "models" / "gemma-3-2b-instruct-Q4_K_M.gguf"
WHISPER_MODEL = AXIOM_DIR / "whisper" / "ggml-medium.bin"
PIPER_MODEL   = AXIOM_DIR / "piper" / "fr_FR-upmc-medium.onnx"
VENV_DIR   = AXIOM_DIR / "venv"
LOG_DIR    = AXIOM_DIR / "logs"
MEMORY_DIR = AXIOM_DIR / "memory"
RAG_DIR    = AXIOM_DIR / "rag"
EVENTS_PIPE = Path("/tmp/axiom-events")

# ── Prompt système ──────────────────────────────────────────
SYSTEM_PROMPT = """Tu es AXIOM, l'assistant IA personnel de Rayane.
Tu es son ami tech de confiance — proche, familier, direct.
Tu parles exclusivement en français.
Tu ne dis jamais "je suis une IA" ou "je suis un assistant".
Tu es AXIOM, point.

Règles d'or :
- Tu tutoies toujours Rayane
- Tu es motivé, dynamique, positif mais honnête
- Tu connais tous ses projets (SPECTRA, Bac Rush, HYPERWORLD...)
- Tu peux exécuter des commandes système (avec prudence)
- Tu ne feras JAMAIS : rm -rf /, mkfs, dd if=..., shutdown non confirmé
- Si une commande est dangereuse, tu demandes confirmation TWICE
- Tu mémorises tout via ton système RAG

Contexte système :
- Machine : ASUS TUF FX507ZU4 (i7-12700H / RTX 4050 6GB)
- OS : Arch Linux + Hyprland HYPERWORLD
- Mondes : Gaming (WS1-3), Cybersec (WS4-6), Prog (WS7-9)
- Projets connus : SPECTRA (ESP32-P4), Bac Rush (React), et plus...
"""

# ── Commandes interdites ────────────────────────────────────
FORBIDDEN_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=/dev/zero of=/dev",
    "dd if=/dev/urandom of=/dev",
    "> /dev/sda",
    "chmod -R 777 /",
    ":(){ :|:& };:",  # fork bomb
    "shutdown",
    "reboot",
]

REQUIRE_CONFIRM = [
    "pacman -R",
    "pacman -Rns",
    "systemctl stop",
    "systemctl disable",
    "rm -rf",
    "sudo rm",
]


# ── Vérification commande ───────────────────────────────────
def is_command_safe(cmd: str) -> tuple[bool, bool, str]:
    """
    Retourne (is_safe, needs_confirm, reason)
    """
    cmd_lower = cmd.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in cmd_lower:
            return False, False, f"COMMANDE INTERDITE : contient '{pattern}'"
    for pattern in REQUIRE_CONFIRM:
        if pattern in cmd_lower:
            return True, True, f"Commande sensible : '{pattern}'"
    return True, False, ""


# ── Exécution sécurisée ─────────────────────────────────────
def execute_command(cmd: str, interactive: bool = True) -> str:
    safe, needs_confirm, reason = is_command_safe(cmd)
    if not safe:
        return f"⛔ {reason}\nRefus d'exécution."
    if needs_confirm and interactive:
        speak(f"Attention, cette commande est sensible : {reason}. Tu confirmes ?")
        confirm = input("  Confirme [oui/non] : ").strip().lower()
        if confirm not in ["oui", "o", "yes"]:
            return "❌ Commande annulée."
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30
        )
        output = result.stdout + result.stderr
        return output[:2000] if output else "✓ Exécuté sans sortie."
    except subprocess.TimeoutExpired:
        return "⏱ Timeout (30s) — commande annulée."
    except Exception as e:
        return f"❌ Erreur : {e}"


# ── TTS — Piper ─────────────────────────────────────────────
def speak(text: str):
    if not PIPER_MODEL.exists():
        print(f"  [AXIOM] {text}")
        return
    try:
        piper_cmd = f'echo "{text}" | piper --model {PIPER_MODEL} --output-raw | aplay -r 22050 -f S16_LE -c 1 -'
        subprocess.Popen(piper_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print(f"  [AXIOM] {text}")


# ── STT — Whisper ───────────────────────────────────────────
def listen_once(timeout: int = 10) -> str:
    """Enregistre et transcrit une phrase"""
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np

        sample_rate = 16000
        print("  🎙 À toi...", end="", flush=True)
        audio = sd.rec(int(timeout * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        print(" ✓")

        tmp_wav = Path("/tmp/axiom_input.wav")
        sf.write(tmp_wav, audio, sample_rate)

        # Transcription avec Whisper
        result = subprocess.run(
            f"whisper {tmp_wav} --model medium --language fr --output-format txt --output-dir /tmp",
            shell=True, capture_output=True, text=True
        )
        txt_file = Path("/tmp/axiom_input.txt")
        if txt_file.exists():
            return txt_file.read_text().strip()
    except Exception as e:
        pass
    return ""


# ── LLM — llama-cpp-python ──────────────────────────────────
class AxiomLLM:
    def __init__(self):
        self.llm = None
        self.loaded = False

    def load(self):
        if self.loaded:
            return
        if not MODEL_PATH.exists():
            print(f"  ⚠ Modèle introuvable : {MODEL_PATH}")
            print(f"  → Lance install.py pour télécharger les modèles")
            return
        try:
            from llama_cpp import Llama
            print("  ⚡ Chargement du modèle AXIOM...", end="", flush=True)
            self.llm = Llama(
                model_path=str(MODEL_PATH),
                n_ctx=8192,
                n_gpu_layers=-1,       # Tout sur GPU (RTX 4050)
                n_threads=8,           # i7-12700H
                verbose=False,
                chat_format="gemma",
            )
            self.loaded = True
            print(" ✓ Prêt !")
        except ImportError:
            print("  ✗ llama-cpp-python non installé. Lance : pip install llama-cpp-python")
        except Exception as e:
            print(f"  ✗ Erreur chargement modèle : {e}")

    def chat(self, messages: list[dict], max_tokens: int = 1024) -> str:
        if not self.llm:
            return "⚠ Modèle non chargé."
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.95,
                repeat_penalty=1.1,
                stop=["<end_of_turn>", "<eos>"],
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"❌ Erreur LLM : {e}"


# ── RAG — ChromaDB ──────────────────────────────────────────
class AxiomRAG:
    def __init__(self):
        self.collection = None

    def init(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(RAG_DIR))
            self.collection = client.get_or_create_collection("axiom_memory")
            print("  ✓ RAG initialisé")
        except Exception as e:
            print(f"  ⚠ RAG non disponible : {e}")

    def remember(self, text: str, metadata: dict = None):
        if not self.collection:
            return
        try:
            import hashlib
            doc_id = hashlib.md5(text.encode()).hexdigest()
            self.collection.upsert(
                documents=[text],
                ids=[doc_id],
                metadatas=[metadata or {"timestamp": datetime.now().isoformat()}]
            )
        except Exception:
            pass

    def recall(self, query: str, n: int = 5) -> str:
        if not self.collection:
            return ""
        try:
            results = self.collection.query(query_texts=[query], n_results=n)
            docs = results.get("documents", [[]])[0]
            return "\n".join(docs) if docs else ""
        except Exception:
            return ""


# ── Session de conversation ─────────────────────────────────
class AxiomSession:
    def __init__(self):
        self.llm   = AxiomLLM()
        self.rag   = AxiomRAG()
        self.history: list[dict] = []
        self.LOG_DIR.mkdir(parents=True, exist_ok=True) if LOG_DIR else None

    @property
    def LOG_DIR(self):
        return AXIOM_DIR / "logs"

    def start(self):
        self.llm.load()
        self.rag.init()
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, user_input: str, voice_out: bool = False) -> str:
        if not user_input.strip():
            return ""

        # Contexte RAG
        context = self.rag.recall(user_input)
        augmented = user_input
        if context:
            augmented = f"[Contexte de ma mémoire:\n{context}]\n\nRayane: {user_input}"

        self.history.append({"role": "user", "content": augmented})
        response = self.llm.chat(self.history)
        self.history.append({"role": "assistant", "content": response})

        # Mémoriser l'échange
        self.rag.remember(f"Rayane: {user_input}\nAXIOM: {response}")

        # Log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "axiom": response,
        }
        log_file = self.LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # Détecter commande à exécuter
        if "```bash" in response or "```shell" in response:
            lines = response.split("\n")
            in_block = False
            commands = []
            for line in lines:
                if "```bash" in line or "```shell" in line:
                    in_block = True
                elif "```" in line and in_block:
                    in_block = False
                elif in_block:
                    commands.append(line.strip())
            if commands:
                print("\n  💻 Commandes à exécuter :")
                for cmd in commands:
                    print(f"    $ {cmd}")
                confirm = input("  Exécuter ? [o/N] : ").strip().lower()
                if confirm == "o":
                    for cmd in commands:
                        output = execute_command(cmd, interactive=False)
                        print(f"  → {output}")

        if voice_out:
            speak(response)

        return response


# ── Mode interactif ─────────────────────────────────────────
def interactive_mode():
    print("""
╔══════════════════════════════════════════════╗
║  AXIOM — Mode interactif                    ║
║  'vocal' → entrée voix / 'exit' → quitter  ║
╚══════════════════════════════════════════════╝
""")
    session = AxiomSession()
    session.start()
    speak("Salut Rayane ! Je suis là, qu'est-ce que je peux faire pour toi ?")

    while True:
        try:
            user_input = input("\n  Toi › ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                speak("À plus Rayane !")
                break
            elif user_input.lower() == "vocal":
                speak("Je t'écoute.")
                user_input = listen_once()
                if not user_input:
                    speak("Je n'ai pas capté, réessaie.")
                    continue
                print(f"  Tu as dit : {user_input}")

            response = session.chat(user_input, voice_out=True)
            print(f"\n  AXIOM › {response}")

        except KeyboardInterrupt:
            speak("À plus Rayane !")
            break
        except EOFError:
            break


# ── Mode daemon ─────────────────────────────────────────────
def daemon_mode():
    print("  AXIOM daemon démarré...")
    session = AxiomSession()
    session.start()

    EVENTS_PIPE.touch()

    def handle_events():
        while True:
            try:
                with open(EVENTS_PIPE) as f:
                    event = f.read().strip()
                if event:
                    open(EVENTS_PIPE, "w").close()
                    if event == "UI_OPEN":
                        response = session.chat("Salut AXIOM, t'es là ?", voice_out=True)
            except Exception:
                pass
            time.sleep(1)

    thread = threading.Thread(target=handle_events, daemon=True)
    thread.start()

    # Garder le daemon vivant
    signal.pause()


# ── Entrée principale ───────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AXIOM — Assistant IA HYPERWORLD")
    parser.add_argument("--daemon",      action="store_true", help="Mode daemon")
    parser.add_argument("--interactive", action="store_true", help="Mode interactif terminal")
    args = parser.parse_args()

    if args.daemon:
        daemon_mode()
    else:
        interactive_mode()
