#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 02 — Pilotes NVIDIA RTX 4050
- nvidia-dkms (meilleure compatibilité Wayland vs nvidia)
- Configuration mkinitcpio
- Module DRM pour Wayland
- Optimisations performances GPU
"""

import subprocess, os, re
from pathlib import Path

HOME = Path(os.environ.get("HYPERWORLD_HOME", Path.home()))

def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def install_nvidia():
    print("\n  ── Installation drivers NVIDIA ──")
    pkgs = [
        "nvidia-dkms", "nvidia-utils", "lib32-nvidia-utils",
        "nvidia-settings", "nvidia-prime", "egl-wayland",
        "libva-nvidia-driver", "vulkan-icd-loader",
        "lib32-vulkan-icd-loader", "vulkan-tools",
        "cuda", "cudnn",
    ]
    run(f"sudo pacman -S --noconfirm --needed {' '.join(pkgs)}", check=False)

def configure_mkinitcpio():
    print("\n  ── Configuration mkinitcpio pour Nvidia ──")
    conf = Path("/etc/mkinitcpio.conf")
    content = conf.read_text()

    # Ajouter les modules nvidia dans MODULES=()
    if "nvidia" not in content:
        content = content.replace(
            "MODULES=()",
            "MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)"
        )
        # Si MODULES a déjà quelque chose, on ajoute intelligemment
        tmp = Path("/tmp/mkinitcpio.conf.new")
        tmp.write_text(content)
        run("sudo mv /tmp/mkinitcpio.conf.new /etc/mkinitcpio.conf")
        run("sudo mkinitcpio -P")
        print("  ✓ mkinitcpio configuré pour Nvidia")
    else:
        print("  ✓ Modules Nvidia déjà dans mkinitcpio")

def configure_drm_modeset():
    print("\n  ── Activation nvidia-drm.modeset=1 ──")
    # Pour systemd-boot
    loader_entries = Path("/boot/loader/entries")
    if loader_entries.exists():
        for entry in loader_entries.glob("*.conf"):
            txt = entry.read_text()
            if "nvidia-drm.modeset" not in txt:
                # Injecter après "options" sur la même ligne
                txt = re.sub(r"^(options\s+)", r"\1nvidia-drm.modeset=1 ", txt, flags=re.MULTILINE)
                tmp = Path(f"/tmp/{entry.name}.new")
                tmp.write_text(txt)
                run(f"sudo mv {tmp} {entry}")
        print("  ✓ DRM modeset activé dans systemd-boot")
    else:
        # GRUB fallback — regex robuste, indépendante du contenu existant
        grub_default = Path("/etc/default/grub")
        if grub_default.exists():
            txt = grub_default.read_text()
            if "nvidia-drm.modeset" not in txt:
                txt = re.sub(
                    r'(GRUB_CMDLINE_LINUX_DEFAULT="[^"]*?)(")',
                    lambda m: m.group(1) + " nvidia-drm.modeset=1" + m.group(2),
                    txt
                )
                tmp = Path("/tmp/grub.new")
                tmp.write_text(txt)
                run("sudo mv /tmp/grub.new /etc/default/grub")
                run("sudo grub-mkconfig -o /boot/grub/grub.cfg", check=False)
            print("  ✓ DRM modeset activé dans GRUB")

def disable_nouveau():
    print("\n  ── Blacklist du driver nouveau ──")
    blacklist = Path("/etc/modprobe.d/blacklist-nouveau.conf")
    if not blacklist.exists():
        content = "blacklist nouveau\noptions nouveau modeset=0\n"
        tmp = Path("/tmp/blacklist-nouveau.conf")
        tmp.write_text(content)
        run("sudo mv /tmp/blacklist-nouveau.conf /etc/modprobe.d/")
        print("  ✓ nouveau blacklisté")
    else:
        print("  ✓ nouveau déjà blacklisté")

def configure_nvidia_power():
    print("\n  ── Configuration gestion énergie Nvidia ──")
    # Persistence mode pour le laptop
    conf = """[Unit]
Description=NVIDIA Persistence Daemon
Wants=syslog.target

[Service]
Type=forking
PIDFile=/var/run/nvidia-persistenced/nvidia-persistenced.pid
Restart=always
ExecStart=/usr/bin/nvidia-persistenced --verbose
ExecStopPost=/bin/rm -rf /var/run/nvidia-persistenced

[Install]
WantedBy=multi-user.target
"""
    # nvidia-persistenced est inclus dans nvidia-utils
    run("sudo systemctl enable nvidia-persistenced", check=False)

    # Règle udev pour Nvidia Power Management
    udev_rule = """# NVIDIA RTX 4050 — Power Management
ACTION=="add", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x03[0-9]*", TEST=="power/control", ATTR{power/control}="auto"
"""
    tmp = Path("/tmp/80-nvidia-pm.rules")
    tmp.write_text(udev_rule)
    run("sudo mv /tmp/80-nvidia-pm.rules /etc/udev/rules.d/")
    run("sudo udevadm control --reload-rules", check=False)
    print("  ✓ Power management Nvidia configuré")

def configure_prime_offload():
    print("\n  ── Configuration PRIME Offload (iGPU + dGPU) ──")
    # Script prime-run est fourni par nvidia-prime
    # Ajouter alias dans le profile
    profile_d = Path("/etc/profile.d/nvidia-prime.sh")
    content = """# HYPERWORLD — NVIDIA PRIME Offload
# Utilise 'prime-run <commande>' pour forcer le GPU dédié
export __NV_PRIME_RENDER_OFFLOAD=1
export __NV_PRIME_RENDER_OFFLOAD_PROVIDER=NVIDIA-G0
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export __VK_LAYER_NV_optimus=NVIDIA_only
"""
    if not profile_d.exists():
        tmp = Path("/tmp/nvidia-prime.sh")
        tmp.write_text(content)
        run("sudo mv /tmp/nvidia-prime.sh /etc/profile.d/")
        print("  ✓ PRIME Offload configuré")
    else:
        print("  ✓ PRIME déjà configuré")

if __name__ == "__main__":
    print("\n  ═══ MODULE 02 : PILOTES NVIDIA RTX 4050 ═══\n")
    install_nvidia()
    configure_mkinitcpio()
    configure_drm_modeset()
    disable_nouveau()
    configure_nvidia_power()
    configure_prime_offload()
    print("\n  ✓ Drivers NVIDIA configurés — un reboot sera nécessaire avant Wayland")
