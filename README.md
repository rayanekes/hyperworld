# 🌌 HYPERWORLD

> Arch Linux + Hyprland Multi-Monde + AXIOM IA — Setup Autonome

## 🚀 Installation en une commande

```bash
git clone https://github.com/rayanekes/hyperworld.git ~/hyperworld
cd ~/hyperworld
python install.py
```

## 🌍 Les 3 Mondes

| Raccourci | Monde | Style |
|---|---|---|
| `Super + F1` | 🎮 Gaming — CIRCUIT NOIR | Magenta/Cyan, cyberpunk |
| `Super + F2` | 🛡️ Cybersec — GHOST PROTOCOL | Vert Matrix, hacker |
| `Super + F3` | 🔬 Prog — DEEP SPACE IDE | Bleu/Orange, productivité |

## ⌨️ Raccourcis essentiels

| Raccourci | Action |
|---|---|
| `Super` | Vue globale toutes apps |
| `Super + A` | Invoquer AXIOM |
| `Super + T` | Terminal |
| `Super + B` | Firefox |
| `Super + Q` | Fermer fenêtre |
| `Super + F` | Fullscreen |
| `Super + V` | Fenêtre flottante |

## 🤖 AXIOM

L'IA hors-ligne, ton ami tech :
- S'active automatiquement quand tu branches le chargeur
- `Super + A` pour l'invoquer manuellement
- Voix masculine française (Piper TTS)
- Reconnait ta voix (Whisper Medium)
- Mémoire permanente (ChromaDB RAG)
- Peut gérer tes fichiers, git, système

## 📁 Structure

```
hyperworld/
├── install.py          ← Lance ça après Arch install
├── state.json          ← Progression (auto-reprise)
├── modules/            ← 11 étapes d'installation
├── packages/           ← Listes de paquets
├── dotfiles/           ← Toutes les configs
└── scripts/            ← Scripts runtime
```

## ⚙️ Prérequis

- Arch Linux installé (base uniquement)
- Connexion internet
- Python 3.11+

## 🔄 Reprise automatique

Si le script est interrompu, il reprend exactement où il s'est arrêté :
```bash
python install.py  # reprend automatiquement
```

---

*HYPERWORLD — Construit pour un seul PC, taillé sur mesure.*
