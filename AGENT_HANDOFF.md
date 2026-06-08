# 🌌 HYPERWORLD — Document de Passation Agent
**Fichier de contexte complet pour reprendre le projet là où on l'a laissé.**
> Rédigé à la fin de la session de conception — 2026-06-08

---

## 🎯 Vision du Projet

**HYPERWORLD** est un environnement Arch Linux + Hyprland entièrement automatisé
et modulaire pour un ASUS TUF FX507ZU4. Ce n'est pas une config Hyprland ordinaire :
c'est un **système multi-monde** où chaque contexte de travail a son propre univers
visuel, ses propres applications et son propre style.

### Les 3 Mondes
| Monde | Workspaces | Thème | Usage |
|---|---|---|---|
| 🎮 **GAMING** "Circuit Noir" | WS 1-3 | Magenta + Cyan néon | Steam, Lutris, Bottles, Discord, Heroic |
| 🛡️ **CYBERSEC** "Ghost Protocol" | WS 4-6 | Vert Matrix + Noir pur | Wireshark, Ghidra, MSF, Nmap, BurpSuite |
| 🔬 **PROG/AI** "Deep Space IDE" | WS 7-9 | Lavande + Teal | VSCode, Arduino, Docker, Jupyter, AXIOM |

### L'Assistant IA — AXIOM
- Nom : **AXIOM** (préférence de Rayane, pas négociable)
- Stack : `llama-cpp-python` (CUDA) + `Whisper.cpp` + `Piper TTS` + `ChromaDB` (RAG)
- Modèle : `gemma-3-2b-instruct Q4_K_M` (sur RTX 4050)
- Langue : **Français uniquement**, tutoiement, proche comme un ami tech
- Activation : `Super+A` ou voix (wake word "axiom")
- Se lance automatiquement quand branché secteur

---

## 💻 Matériel cible

```
Machine    : ASUS TUF Gaming FX507ZU4
CPU        : Intel Core i7-12700H (12C/20T — 6P + 8E cores)
GPU        : NVIDIA GeForce RTX 4050 6GB (CUDA 12.x)
RAM        : 16 GB DDR5
Stockage   : 512 GB NVMe SSD
Écran      : 15.6" FHD 1920×1080 @ 144Hz (intégré uniquement)
Audio      : PipeWire
Réseau     : WiFi + Ethernet (iwd + NetworkManager)
OS actuel  : Pop!_OS (sera supprimé pour Arch)
```

---

## 📁 Structure du Projet

```
~/hyperworld/                  ← Repo GitHub : rayanekes/hyperworld
├── install.py                 ← Orchestrateur principal (state machine)
├── bootstrap.sh               ← Premier script à lancer sur Arch frais
├── README.md
├── .gitignore
├── modules/
│   ├── 01_base_arch.py        ← Pacman, paru (AUR), multilib, miroirs
│   ├── 02_nvidia_drivers.py   ← nvidia-dkms, DRM modeset, PRIME offload
│   ├── 03_audio_network.py    ← PipeWire, NM+iwd, Bluetooth
│   ├── 04_hyprland_core.py    ← Hyprland stack, SDDM, fonts, fzf-tab, HyperBoard deps
│   ├── 05_world_system.py     ← Scripts world-switch, global-overview, power-monitor
│   ├── 06_apps_gaming.py      ← Steam, Wine, Lutris, Bottles, Heroic, GameMode
│   ├── 07_apps_cybersec.py    ← Wireshark, Ghidra, MSF, Hydra, Tor, Nmap...
│   ├── 08_apps_prog.py        ← VSCode, Arduino IDE, Docker, CUDA, PyTorch
│   ├── 09_ai_stack.py         ← llama-cpp-python CUDA, Whisper.cpp, Piper, ChromaDB
│   ├── 10_dotfiles.py         ← Déploiement symlinks de tout dotfiles/
│   └── 11_finalize.py         ← Vérifications finales, services, guide rapide
├── dotfiles/
│   ├── hyprland/
│   │   ├── hyprland.conf      ← Config principale (monitor, general, input)
│   │   ├── animations.conf    ← Courbes premium (overshoot, cinematic, snap)
│   │   ├── keybinds.conf      ← Tous les raccourcis (worlds, AXIOM, screenshots...)
│   │   ├── windowrules.conf   ← Isolation fenêtres par monde
│   │   ├── autostart.conf     ← swww, waybar, swaync, HyperBoard daemon, hypridle
│   │   ├── active_world.conf  ← Config monde actif (symlink dynamique)
│   │   ├── hyprlock.conf      ← Écran verrou (horloge Orbitron, blur intense)
│   │   ├── hypridle.conf      ← Gestion inactivité (luminosité→lock→dpms off)
│   │   └── worlds/
│   │       ├── gaming.conf    ← Bordures magenta, ombres roses, overshoot
│   │       ├── cybersec.conf  ← Bordures vert Matrix, arrondis petits, snap
│   │       └── prog.conf      ← Bordures lavande/teal, blur max, premium
│   ├── waybar/
│   │   ├── gaming/            ← config.jsonc + style.css magenta/cyan
│   │   ├── cybersec/          ← config.jsonc + style.css vert Matrix
│   │   └── prog/              ← config.jsonc + style.css lavande glassmorphism
│   ├── kitty/
│   │   ├── gaming.conf        ← Palette magenta, Hack Nerd Font
│   │   ├── cybersec.conf      ← Vert Matrix, noir pur, opacité 0.96
│   │   └── prog.conf          ← Deep Space IDE, CaskaydiaCove, ligatures
│   ├── rofi/
│   │   ├── global-overview.rasi  ← Vue toutes apps (Super+Shift)
│   │   └── world-launcher.rasi   ← Apps du monde actif (Super+Space)
│   ├── swaync/
│   │   ├── config.json        ← Position, grouping, DND
│   │   └── style.css          ← Glassmorphism, urgences colorées
│   ├── swappy/
│   │   └── config             ← Sauvegarde auto ~/Pictures/Screenshots/
│   ├── hyperboard/
│   │   ├── hyperboard.py      ← App GTK4+WebKit2 (daemon Wayland layer shell)
│   │   ├── index.html         ← Structure 3 colonnes
│   │   ├── style.css          ← Design premium dynamique par monde
│   │   └── app.js             ← Horloge, particules, IPC Python↔JS, données
│   ├── axiom/
│   │   ├── axiom.py           ← Daemon AXIOM : LLM+STT+TTS+RAG+executor
│   │   ├── config.yaml        ← Toute la config AXIOM (chemins, paramètres)
│   │   └── system_prompt.md   ← Personnalité, règles, contexte Rayane
│   ├── starship.toml          ← Prompt ZSH premium (git, python, node, batterie)
│   └── zshrc                  ← ZSH complet : fzf-tab, 40+ alias, fonctions
├── scripts/
│   ├── world-switch.sh        ← Change de monde (wallpaper+waybar+kitty+hyprland)
│   ├── global-overview.sh     ← Rofi toutes apps
│   ├── axiom-launch.sh        ← Lance/toggle AXIOM terminal
│   ├── power-monitor.sh       ← Surveille secteur/batterie → gère AXIOM
│   ├── hyperboard-launch.sh   ← Toggle HyperBoard via signal fichier
│   ├── screenshot.sh          ← 5 modes : area/full/copy/window/gallery
│   └── get-wallpapers.sh      ← Télécharge wallpapers Unsplash + fallback ImageMagick
└── packages/
    ├── base.txt               ← Paquets base système
    ├── wayland.txt            ← Stack Wayland
    ├── gaming.txt             ← Paquets gaming
    ├── cybersec.txt           ← Outils sécurité
    ├── prog.txt               ← Outils développement
    └── models.json            ← URLs modèles IA (GGUF, Whisper, Piper)
```

---

## 🔧 Comment ça marche — Flux d'installation

### 1. Sur l'Arch tout frais (après archinstall)
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/rayanekes/hyperworld/main/bootstrap.sh)
```
`bootstrap.sh` :
1. Optimise les miroirs pacman (France/Allemagne/Espagne)
2. Met à jour le système (`pacman -Syu`)
3. Installe : python, git, wget, curl, base-devel
4. Vérifie la connexion internet
5. Clone le repo dans `~/hyperworld`
6. Lance `python install.py`

### 2. `install.py` — La state machine
- Utilise `state.json` pour reprendre si interrompu
- Exécute les modules 01 à 11 dans l'ordre
- Chaque module est idempotent (peut être relancé)
- Logs dans `~/.hyperworld-install.log`
- Affiche progression, erreurs, et attend les téléchargements

### 3. Changement de monde (runtime)
```bash
world-switch.sh gaming    # ou cybersec, prog
```
Le script :
1. Change le symlink `active_world.conf` → `worlds/gaming.conf`
2. Change `~/.config/waybar/` → `waybar/gaming/`
3. Change `~/.config/kitty/kitty.conf` → `kitty/gaming.conf`
4. Change le wallpaper via swww (transition fade 144fps)
5. Recharge Waybar et Hyprland
6. Notifie AXIOM du changement de monde

---

## 🎮 HyperBoard (Super Key Dashboard)

Dashboard animé qui s'ouvre sur la touche Super.
- **Technologie** : Python + GTK4 + WebKit2GTK (Wayland layer shell, plein écran)
- **Colonne gauche** : Switcher de mondes, apps rapides du monde actif, AXIOM card, contrôles Spotify
- **Centre** : Horloge Orbitron géante, météo Alger (wttr.in), 8 actus HackerNews live, 4 jeux recommandés par monde
- **Droite** : Barres CPU/RAM/GPU animées, VRAM RTX 4050, batterie, raccourcis clavier
- **Fond** : Particules canvas connectées, couleur adaptée au monde actif
- **IPC** : JS → Python via `webkit.messageHandlers.hyperboard`
- **Daemon** : Lancé au boot (`autostart.conf`), toggle via signal fichier `/tmp/hyperboard-toggle`

---

## 📸 Screenshot Manager

Script unifié `screenshot.sh` avec 5 modes :
| Raccourci | Mode | Action |
|---|---|---|
| `Print` | `area` | Sélection zone + swappy (annotation) → sauvegardé + copié |
| `Shift+Print` | `full` | Écran entier + swappy |
| `Super+Print` | `copy` | Zone → presse-papier sans fenêtre |
| `Ctrl+Print` | `window` | Fenêtre active (géométrie via hyprctl) |
| `Super+Alt+Print` | `gallery` | Galerie fzf avec aperçu, Ctrl+D supprime, Ctrl+Y copie |

Sauvegarde : `~/Pictures/Screenshots/hw-TIMESTAMP.png`
Notification avec miniature automatique.

---

## ⌨️ Complétion Terminal

`fzf-tab` installé via AUR (`zsh-fzf-tab`) — remplace Tab par un menu fzf :
- **Tab sur fichier** → aperçu bat en temps réel
- **Tab sur `kill`** → aperçu processus
- **Tab sur `systemctl`** → status du service
- **Ctrl+R** → historique avec aperçu + Ctrl+Y copie
- **Ctrl+T** → chercher fichiers avec aperçu bat 55%
- **Alt+C** → naviguer dossiers avec arbre eza

---

## 👤 Préférences de Rayane (CRITIQUE — à respecter)

### Style & Esthétique
- **Animations partout, absolument tout** doit être animé
- Préfère les fenêtres qui "rebondissent" sur les côtés (overshoot/spring)
- Déteste les animations basiques et lourdes
- Interface "premium" — pas de placeholder, pas de rigide
- Police Orbitron pour les titres (déjà configurée)

### Applications confirmées
- **IDE** : VSCode + Antigravity (son IA de code = Gemini)
- **Terminal** : Kitty
- **Musique** : Spotify Premium
- **Browser** : Firefox
- **Jeux** : PES/eFootball, Genshin Impact, RDR2, AC Mirage

### AXIOM (l'assistant)
- **Toujours en français**, tutoiement
- Personnalité : ami tech motivant, direct, pas condescendant
- Bridé : refuse `rm -rf /`, `mkfs`, `dd if=/dev/zero`, fork bombs
- Double confirmation : `sudo rm -rf`, `pacman -Rns`, `shutdown`
- Connaît tous les projets de Rayane (RAG indexe ses dossiers)
- **Projets connus** : SPECTRA (ESP32 cyber-warfare), Sylvan (jeu RPG ESP32), Bac Rush (React), HYPERWORLD

### Ce que Rayane n'aime pas
- Trucs rigides et statiques
- Animations basiques
- Interface "minimaliste" au sens vide
- Pop!_OS (il le supprime pour Arch)
- La complétion ZSH basique (maintenant remplacée par fzf-tab)

---

## 📊 État actuel (100% complet)

```
✅ Modules installation  11/11
✅ Configs Hyprland       5 fichiers
✅ Configs par monde      3×3 fichiers (waybar/kitty/worlds)
✅ Scripts runtime        7 scripts
✅ AXIOM stack            3 fichiers (daemon + config + prompt)
✅ HyperBoard             4 fichiers (py + html + css + js)
✅ Rofi thèmes            2 fichiers
✅ swaync                 2 fichiers
✅ Screenshots            config + script
✅ ZSH + Starship         2 fichiers
✅ Bootstrap              1 fichier
✅ README + .gitignore    2 fichiers
✅ GitHub push            github.com/rayanekes/hyperworld (main)

Total : 158 fichiers
```

---

## ⚠️ Points de vigilance pour l'installation réelle

### 1. CUDA (~4GB) prend du temps
Le module `08_apps_prog.py` installe `cuda` + `cudnn` depuis les repos Arch officiels.
C'est normal, ça peut prendre 15-30 min selon la connexion.

### 2. llama-cpp-python se compile (5-10 min)
Le module `09_ai_stack.py` compile llama-cpp-python avec les flags CUDA.
Ne pas interrompre cette étape.

### 3. Modèles IA
Téléchargés dans `~/.axiom/models/` :
- `gemma-3-2b-instruct-Q4_K_M.gguf` (~1.7 GB)
- `ggml-medium.bin` Whisper (~1.5 GB)
- `fr_FR-upmc-medium.onnx` Piper (~60 MB)

Vérifier les URLs dans `packages/models.json` avant de lancer.

### 4. SDDM et session Hyprland
Après installation, le premier reboot lance SDDM.
Sélectionner "Hyprland" dans la liste des sessions.

### 5. PRIME offload (GPU discret)
Le RTX 4050 est en mode PRIME. Pour lancer un jeu sur le GPU :
```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia %command%
```
Cette variable est configurée dans Steam via les options de lancement.

### 6. HyperBoard nécessite webkit2gtk-4.1
Installé par `04_hyprland_core.py`. Si absente : `sudo pacman -S webkit2gtk-4.1`

### 7. fzf-tab via AUR
Installé par `paru -S zsh-fzf-tab`. Si paru pas encore installé au moment de la config ZSH → le module 01 l'installe en premier.

---

## 🔄 Ce qu'un agent peut améliorer / continuer

### Améliorations possibles (en ordre de priorité)

1. **Tester et débugger post-installation**
   - Vérifier que tous les scripts s'exécutent sans erreur sur Arch réel
   - Tester le passage entre mondes (world-switch.sh)
   - Vérifier que HyperBoard s'ouvre correctement (WebKit + layer shell)

2. **AXIOM — améliorer la reconnaissance vocale**
   - Tester le pipeline STT → LLM → TTS en conditions réelles
   - Calibrer le `silence_threshold` dans `config.yaml`
   - Ajouter un indicateur visuel quand AXIOM écoute (overlay waybar)

3. **world-switch.sh — vérifier la logique des symlinks**
   - Le script `05_world_system.py` génère world-switch.sh
   - À vérifier : les chemins vers les configs sont bien absolus

4. **Fonds d'écran alternatifs**
   - Rayane peut vouloir ses propres wallpapers
   - Les mettre dans `~/hyperworld/dotfiles/wallpapers/` et relancer `get-wallpapers.sh`

5. **HyperBoard — amélioration données**
   - Ajouter une source d'actus tech en français (ex: Le Monde Tech RSS)
   - Ajouter un historique de conversation AXIOM dans la colonne droite

6. **Rofi world-launcher — icônes d'apps**
   - Actuellement utilise les icônes GTK par défaut
   - Peut être amélioré avec des icônes custom

---

## 🚀 Commande de déploiement final

```bash
# Sur Arch Linux fraîchement installé (post archinstall, en session utilisateur)
bash <(curl -fsSL https://raw.githubusercontent.com/rayanekes/hyperworld/main/bootstrap.sh)
```

Ou si déjà cloné :
```bash
cd ~/hyperworld && python install.py
```

---

## 📬 Contexte GitHub

```
Repo    : https://github.com/rayanekes/hyperworld
User    : rayanekes
Branch  : main
Commits :
  ba6f672 — v1.1 — HyperBoard, fzf-tab, screenshot manager
  29859b3 — v1.0 — Arch + Hyprland + AXIOM
```

---

*Ce fichier est placé dans le repo (`AGENT_HANDOFF.md`) et dans les artifacts de l'agent précédent.*
*Dernière mise à jour : 2026-06-08 par l'agent de conception HYPERWORLD.*
