#!/usr/bin/env python3
"""
unbego_flash.py - Flash / Unbrick Module
Handles the actual unbricking process for Redmi Note 8 Pro (MT6785)
using mtkclient via termux-usb file descriptor passing.
"""

import subprocess
import os
import sys
import json

MTKCLIENT_DIR = os.path.expanduser("~/mtkclient")

CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
NC = "\033[0m"


def check_mtkclient():
    """Check if mtkclient is installed."""
    if not os.path.isdir(MTKCLIENT_DIR):
        print(f"  {RED}[✗] mtkclient not found at {MTKCLIENT_DIR}{NC}")
        print(f"  {YELLOW}    Run ./setup-unbego.sh to install it.{NC}")
        return False
    mtk_script = os.path.join(MTKCLIENT_DIR, "mtk")
    if not os.path.isfile(mtk_script):
        mtk_script = os.path.join(MTKCLIENT_DIR, "mtk.py")
        if not os.path.isfile(mtk_script):
            print(f"  {RED}[✗] mtk/mtk.py script not found in {MTKCLIENT_DIR}{NC}")
            return False
    return True


def get_mtk_cmd():
    """Get the correct mtkclient command."""
    mtk_script = os.path.join(MTKCLIENT_DIR, "mtk")
    if os.path.isfile(mtk_script):
        return f"python {mtk_script}"
    mtk_py = os.path.join(MTKCLIENT_DIR, "mtk.py")
    if os.path.isfile(mtk_py):
        return f"python {mtk_py}"
    return None


def request_usb_permission(device_path):
    """Use termux-usb to request USB permission from Android and run mtkclient."""
    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  USB PERMISSION REQUEST{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {YELLOW}[*] Requesting USB permission for: {device_path}{NC}")
    print(f"  {YELLOW}    An Android popup will appear. Tap 'OK' to grant access.{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")

    # termux-usb -r requests permission, -e runs a script with the FD
    # We'll create a small helper that sets the ANDROID_FD env var
    return device_path


# ═══════════════════════════════════════════════════════
# QUICK FIX — Zero-Download Operations
# These use only mtkclient BROM commands, no firmware files needed
# ═══════════════════════════════════════════════════════

def unlock_bootloader(device_path):
    """Unlock bootloader via BROM security bypass. Zero downloads needed."""
    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  UNLOCK BOOTLOADER (via BROM bypass){NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Downloads needed:{NC} NONE")
    print(f"  {YELLOW}[*] This bypasses Xiaomi's SLA/DAA auth check{NC}")
    print(f"  {YELLOW}    and unlocks the bootloader without a Mi account.{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_unlock.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Bypassing BROM security and unlocking bootloader..."\n')
        f.write('python mtk da seccfg unlock\n')
        f.write('echo ""\n')
        f.write('echo "[✓] Bootloader unlocked."\n')
        f.write('echo "[*] You can now flash custom ROMs or use fastboot."\n')
        f.write('echo "[*] Reboot the phone to apply."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def quick_fix_boot(device_path):
    """Fix common bootloop by erasing problematic partitions. Zero downloads.
    
    Erases: cache, metadata, userdata (factory reset via BROM).
    This fixes: encryption errors, data corruption bootloops, 
    failed OTA updates, and MIUI stuck-on-logo issues.
    """
    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  QUICK FIX — BOOTLOOP REPAIR{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Downloads needed:{NC} NONE")
    print(f"  {YELLOW}[*] This performs a deep factory reset via BROM mode.{NC}")
    print(f"  {YELLOW}    Erases: cache, metadata, userdata{NC}")
    print(f"  {YELLOW}    Fixes: encryption errors, data corruption,{NC}")
    print(f"  {YELLOW}           failed OTA, stuck on MIUI logo{NC}")
    print(f"  {RED}[!] WARNING: All user data will be erased.{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_quick_fix.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Quick Fix — Erasing problematic partitions..."\n')
        f.write('echo ""\n')
        f.write('echo "[*] Erasing cache..."\n')
        f.write('python mtk e cache\n')
        f.write('echo "[*] Erasing metadata (encryption)..."\n')
        f.write('python mtk e metadata\n')
        f.write('echo "[*] Erasing userdata (factory reset)..."\n')
        f.write('python mtk e userdata\n')
        f.write('echo ""\n')
        f.write('echo "[✓] Done. Rebooting device..."\n')
        f.write('python mtk reset\n')
        f.write('echo "[✓] The phone should now boot to MIUI setup screen."\n')
        f.write('echo "    First boot may take 5-10 minutes."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def backup_partitions(device_path, output_dir="~/unbego_backup"):
    """Backup critical partitions before flashing."""
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  PARTITION BACKUP{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Output:{NC} {output_dir}")
    print(f"  {YELLOW}[*] Backing up critical partitions...{NC}")
    print(f"  {YELLOW}    Includes: IMEI (nvram/nvdata/nvcfg), boot, recovery, preloader,{NC}")
    print(f"  {YELLOW}    lk, proinfo, seccfg, protect1/2, persist{NC}")

    partitions = [
        "preloader", "lk", "lk2", "boot", "recovery", "dtbo", "logo",
        "vbmeta", "tee1", "scp1", "sspm_1", "md1img",
        "nvram", "nvdata", "nvcfg", "proinfo", "seccfg",
        "protect1", "protect2", "persist",
    ]

    # Create the termux-usb wrapper script
    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_backup.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        for part in partitions:
            outfile = os.path.join(output_dir, f"{part}.img")
            f.write(f'echo "[*] Backing up {part}..."\n')
            f.write(f'python mtk r {part} {outfile}\n')
        f.write(f'echo "[✓] Backup complete."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command to start the backup:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def flash_scatter(device_path, scatter_file):
    """Flash using a scatter file (SP Flash Tool format)."""
    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  FLASH FIRMWARE (Scatter){NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Scatter File:{NC} {scatter_file}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_flash_scatter.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write(f'echo "[*] Flashing firmware using scatter file..."\n')
        f.write(f'python mtk w "{scatter_file}"\n')
        f.write(f'echo "[✓] Flash complete."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command to flash:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def flash_partition(device_path, partition_name, image_file):
    """Flash a single partition image."""
    if not os.path.isfile(image_file):
        print(f"  {RED}[✗] Image file not found: {image_file}{NC}")
        return False

    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  FLASH PARTITION{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Partition:{NC} {partition_name}")
    print(f"  {GREEN}Image:{NC}     {image_file}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_flash_part.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write(f'echo "[*] Flashing {partition_name}..."\n')
        f.write(f'python mtk w {partition_name} "{image_file}"\n')
        f.write(f'echo "[✓] Flash complete. You can now reboot the device."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command to flash:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def print_gpt(device_path):
    """Print the GPT (GUID Partition Table) from the device."""
    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  READ PARTITION TABLE (GPT){NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {YELLOW}[*] Reading GPT from device via BROM...{NC}")
    print(f"  {YELLOW}    This shows all partitions, offsets, and sizes.{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_print_gpt.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Reading GPT partition table..."\n')
        f.write('python mtk printgpt\n')
        f.write('echo ""\n')
        f.write('echo "[✓] GPT read complete."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def backup_gpt(device_path, output_dir="~/unbego_backup"):
    """Backup the GPT partition table to a file."""
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  BACKUP PARTITION TABLE (GPT){NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Output:{NC} {output_dir}")
    print(f"  {YELLOW}[*] Saving GPT backup...{NC}")
    print(f"  {YELLOW}    Files: gpt_main.bin, gpt_backup.bin{NC}")

    gpt_main = os.path.join(output_dir, "gpt_main.bin")
    gpt_backup = os.path.join(output_dir, "gpt_backup.bin")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_backup_gpt.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Backing up primary GPT..."\n')
        f.write(f'python mtk r gpt {gpt_main}\n')
        f.write('echo "[*] Backing up secondary GPT..."\n')
        f.write(f'python mtk r sgpt {gpt_backup}\n')
        f.write(f'echo "[✓] GPT backup saved to {output_dir}"\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def restore_gpt(device_path, gpt_file):
    """Restore the GPT partition table from a backup file."""
    if not os.path.isfile(gpt_file):
        print(f"  {RED}[✗] GPT backup file not found: {gpt_file}{NC}")
        return False

    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  RESTORE PARTITION TABLE (GPT){NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Source:{NC}   {gpt_file}")
    print(f"  {RED}[!] WARNING: Writing a wrong GPT can permanently brick the device.{NC}")
    print(f"  {RED}    Only use a GPT backup from the SAME device or an identical model.{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_restore_gpt.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Restoring GPT partition table..."\n')
        f.write(f'python mtk w gpt "{gpt_file}"\n')
        f.write('echo "[✓] GPT restored. The device should now recognize all partitions."\n')
        f.write('echo "[*] You may now flash firmware partitions (boot, system, etc.)"\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def rebuild_gpt_from_scatter(device_path, scatter_file):
    """Rebuild the GPT partition table from a scatter file.
    
    This is the nuclear option for devices with completely destroyed
    partition tables. The scatter file contains the partition layout
    for the Redmi Note 8 Pro (MT6785) and mtkclient can use it to
    reconstruct a valid GPT.
    """
    if not os.path.isfile(scatter_file):
        print(f"  {RED}[✗] Scatter file not found: {scatter_file}{NC}")
        return False

    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  REBUILD PARTITION TABLE FROM SCATTER{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Scatter:{NC}  {scatter_file}")
    print(f"  {YELLOW}[*] This will reconstruct the GPT from scratch using{NC}")
    print(f"  {YELLOW}    the partition layout defined in the scatter file.{NC}")
    print(f"  {RED}[!] WARNING: This reformats the entire partition table.{NC}")
    print(f"  {RED}    All partition data will be inaccessible until re-flashed.{NC}")

    # Ask for preloader path (needed when GPT is destroyed)
    print(f"  {YELLOW}[*] When GPT is destroyed, mtkclient needs the preloader{NC}")
    print(f"  {YELLOW}    and scatter file to know the memory map.{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_rebuild_gpt.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Rebuilding GPT using scatter file + preloader..."\n')
        f.write('echo "[*] This uses --scatter flag since the on-device GPT is destroyed."\n')
        f.write(f'python mtk wl "{os.path.dirname(scatter_file)}" --scatter "{scatter_file}"\n')
        f.write('echo ""\n')
        f.write('echo "[✓] GPT rebuilt and partitions written."\n')
        f.write('echo "[*] If this failed, try adding: --preloader preloader_begonia.bin"\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def erase_frp(device_path):
    """Erase the FRP (Factory Reset Protection) partition."""
    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  ERASE FRP (Factory Reset Protection){NC}")
    print(f"{CYAN}{'═' * 50}{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_erase_frp.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Erasing FRP partition..."\n')
        f.write('python mtk e frp\n')
        f.write('echo "[✓] FRP erased."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def reset_nvram(device_path):
    """Reset NVRAM (fixes baseband, IMEI issues after unbrick)."""
    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        return False

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  FORMAT NVRAM/NVCFG{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {RED}[!] WARNING: This will erase IMEI and baseband data.{NC}")
    print(f"  {RED}    Only do this if you have a backup or know how to restore IMEI.{NC}")

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_reset_nvram.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo "[*] Formatting nvram and nvcfg..."\n')
        f.write('python mtk e nvram\n')
        f.write('python mtk e nvcfg\n')
        f.write('echo "[✓] NVRAM reset complete."\n')
    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Run this command:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


def full_unbrick(device_path, firmware_dir):
    """Run the complete 7-phase unbrick sequence for Redmi Note 8 Pro.
    
    Uses the research-backed partition flash order:
    Phase 1: Backup critical partitions (IMEI/calibration)
    Phase 2: Unlock bootloader via BROM
    Phase 3: Flash low-level boot firmware (lk, tee, scp, sspm, md1img, logo)
    Phase 4: Flash kernel & recovery (boot, recovery, dtbo, vbmeta)
    Phase 5: Flash OS (super or system+vendor, cust, erase userdata)
    Phase 6: Preloader (only if user confirms)
    Phase 7: Reset & boot
    """
    firmware_dir = os.path.expanduser(firmware_dir)
    if not os.path.isdir(firmware_dir):
        print(f"  {RED}[✗] Firmware directory not found: {firmware_dir}{NC}")
        return False

    mtk_cmd = get_mtk_cmd()
    if not mtk_cmd:
        print(f"  {RED}[✗] mtkclient not found.{NC}")
        return False

    backup_dir = os.path.expanduser("~/unbego_backup")
    os.makedirs(backup_dir, exist_ok=True)

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  FULL UNBRICK — REDMI NOTE 8 PRO{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"  {GREEN}Firmware Dir:{NC}  {firmware_dir}")
    print(f"  {GREEN}Backup Dir:{NC}    {backup_dir}")
    print(f"  {YELLOW}[*] This will run the complete 7-phase unbrick{NC}")
    print(f"  {YELLOW}    sequence. A single wrapper script is generated{NC}")
    print(f"  {YELLOW}    for termux-usb.{NC}")

    # Check for super.img to determine Android version
    has_super = os.path.isfile(os.path.join(firmware_dir, "super.img"))

    wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unbego_full_unbrick.sh")
    with open(wrapper, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("set -e\n")
        f.write(f"cd {MTKCLIENT_DIR}\n")
        f.write('echo ""\n')
        f.write('echo "========================================"\n')
        f.write('echo "  UNBEGO — FULL UNBRICK SEQUENCE"\n')
        f.write('echo "  Redmi Note 8 Pro (begonia / MT6785)"\n')
        f.write('echo "========================================"\n')

        # Phase 1: Backup
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 1: Backing up critical partitions (IMEI/calibration)..."\n')
        critical = ["nvram", "nvdata", "nvcfg", "proinfo", "persist", "seccfg", "protect1", "protect2"]
        parts_str = ",".join(critical)
        files_str = ",".join([os.path.join(backup_dir, f"{p}.bin") for p in critical])
        f.write(f'python mtk r {parts_str} {files_str}\n')
        f.write(f'echo "[✓] Backup saved to {backup_dir}"\n')

        # Phase 2: Unlock
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 2: Unlocking bootloader via BROM bypass..."\n')
        f.write('python mtk da seccfg unlock\n')
        f.write('echo "[✓] Bootloader unlocked."\n')

        # Phase 3: Low-level boot firmware
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 3: Flashing low-level boot firmware..."\n')
        phase3 = [
            ("lk", "lk.img"), ("lk2", "lk.img"),
            ("dtbo", "dtbo.img"),
            ("tee1", "tee.img"), ("tee2", "tee.img"),
            ("scp1", "scp.img"), ("scp2", "scp.img"),
            ("sspm_1", "sspm.img"), ("sspm_2", "sspm.img"),
            ("md1img", "md1img.img"),
            ("logo", "logo.img"),
        ]
        for part, img in phase3:
            img_path = os.path.join(firmware_dir, img)
            f.write(f'if [ -f "{img_path}" ]; then\n')
            f.write(f'  echo "  [*] Flashing {part}..."\n')
            f.write(f'  python mtk w {part} "{img_path}"\n')
            f.write(f'else\n')
            f.write(f'  echo "  [!] Skipping {part} ({img} not found)"\n')
            f.write(f'fi\n')

        # Phase 4: Kernel & Recovery
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 4: Flashing kernel & recovery..."\n')
        phase4 = [
            ("boot", "boot.img"),
            ("recovery", "recovery.img"),
            ("vbmeta", "vbmeta.img"),
        ]
        for part, img in phase4:
            img_path = os.path.join(firmware_dir, img)
            f.write(f'if [ -f "{img_path}" ]; then\n')
            f.write(f'  echo "  [*] Flashing {part}..."\n')
            f.write(f'  python mtk w {part} "{img_path}"\n')
            f.write(f'else\n')
            f.write(f'  echo "  [!] Skipping {part} ({img} not found)"\n')
            f.write(f'fi\n')

        # Phase 5: OS
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 5: Flashing OS partitions..."\n')
        if has_super:
            f.write(f'echo "  [*] Detected super.img — Android 10/11 layout"\n')
            super_path = os.path.join(firmware_dir, "super.img")
            f.write(f'echo "  [*] Flashing super (this is the largest partition, be patient)..."\n')
            f.write(f'python mtk w super "{super_path}"\n')
        else:
            f.write('echo "  [*] No super.img — using legacy Android 9 layout"\n')
            for part, img in [("system", "system.img"), ("vendor", "vendor.img")]:
                img_path = os.path.join(firmware_dir, img)
                f.write(f'if [ -f "{img_path}" ]; then\n')
                f.write(f'  echo "  [*] Flashing {part}..."\n')
                f.write(f'  python mtk w {part} "{img_path}"\n')
                f.write(f'fi\n')

        cust_path = os.path.join(firmware_dir, "cust.img")
        f.write(f'if [ -f "{cust_path}" ]; then\n')
        f.write(f'  echo "  [*] Flashing cust..."\n')
        f.write(f'  python mtk w cust "{cust_path}"\n')
        f.write(f'fi\n')

        f.write('echo "  [*] Erasing userdata (factory reset)..."\n')
        f.write('python mtk e userdata\n')
        f.write('echo "  [*] Erasing metadata..."\n')
        f.write('python mtk e metadata\n')

        # Phase 6: Preloader warning
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 6: Preloader"\n')
        f.write('echo "  [!] Preloader was NOT flashed (safety precaution)."\n')
        f.write('echo "  [!] Only flash preloader if the device is completely dead."\n')
        f.write('echo "  [!] To flash manually: python mtk w preloader preloader_begonia.bin"\n')

        # Phase 7: Reset
        f.write('echo ""\n')
        f.write('echo "▶ PHASE 7: Rebooting device..."\n')
        f.write('python mtk reset\n')
        f.write('echo ""\n')
        f.write('echo "========================================"\n')
        f.write('echo "  [✓] UNBRICK COMPLETE!"\n')
        f.write('echo "  The phone should now boot to MIUI setup."\n')
        f.write('echo "  First boot may take 5-10 minutes."\n')
        f.write('echo "========================================"\n')

    os.chmod(wrapper, 0o755)

    print(f"\n  {GREEN}Generated full unbrick script.{NC}")
    print(f"  {GREEN}Partitions detected:{NC} {'super (Android 10/11)' if has_super else 'system+vendor (Android 9)'}")
    print(f"\n  {GREEN}Run this command to start:{NC}")
    print(f"  {BOLD}termux-usb -r -e {wrapper} {device_path}{NC}")
    print(f"\n  {RED}[!] This will ERASE userdata (factory reset).{NC}")
    print(f"  {RED}[!] IMEI/calibration will be backed up to {backup_dir}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}\n")
    return True


if __name__ == "__main__":
    if check_mtkclient():
        print(f"{GREEN}[✓] mtkclient is ready.{NC}")
    else:
        print(f"{RED}[✗] mtkclient is not installed.{NC}")

