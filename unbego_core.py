#!/usr/bin/env python3
"""
unbego_core.py - Main Unbego Tool
Interactive CLI for unbricking Redmi Note 8 Pro (MT6785) from Termux.
No root required - uses termux-usb for USB OTG permission handling.
"""

import sys
import os
import time

# Add script directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from unbego_host import get_host_info, print_host_info
from unbego_detect import smart_scan_usb, wait_for_device, get_term_width
from unbego_flash import (
    check_mtkclient,
    backup_partitions,
    flash_partition,
    flash_scatter,
    erase_frp,
    reset_nvram,
    print_gpt,
    backup_gpt,
    restore_gpt,
    rebuild_gpt_from_scatter,
    full_unbrick,
    unlock_bootloader,
    quick_fix_boot,
)
from unbego_adb import adb_menu

# ── Colors ──────────────────────────────────────────────
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
DIM = "\033[2m"
NC = "\033[0m"

VERSION = "1.0.0"

DEVICE_NAME = "Redmi Note 8 Pro"
DEVICE_CODENAME = "begonia"
DEVICE_CHIPSET = "MT6785 (Helio G90T)"


def banner():
    print(f"{CYAN}")
    print("  ██╗   ██╗███╗   ██╗██████╗ ███████╗ ██████╗  ██████╗ ")
    print("  ██║   ██║████╗  ██║██╔══██╗██╔════╝██╔════╝ ██╔═══██╗")
    print("  ██║   ██║██╔██╗ ██║██████╔╝█████╗  ██║  ███╗██║   ██║")
    print("  ██║   ██║██║╚██╗██║██╔══██╗██╔══╝  ██║   ██║██║   ██║")
    print("  ╚██████╔╝██║ ╚████║██████╔╝███████╗╚██████╔╝╚██████╔╝")
    print("   ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝ ")
    print(f"{NC}")
    print(f"  {BOLD}Redmi Note 8 Pro Unbrick Tool{NC} v{VERSION}")
    print(f"  {DIM}Target: {DEVICE_NAME} ({DEVICE_CODENAME}) | {DEVICE_CHIPSET}{NC}")
    print(f"  {DIM}Platform: Termux (No Root Required){NC}")
    print()


def menu():
    w = get_term_width()
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {BOLD}MAIN MENU{NC}")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {GREEN}1{NC}) Detect Host Phone (this device)")
    print(f"  {GREEN}2{NC}) Smart Scan & Connect Device (Auto-Detect Mode)")
    print(f"  {GREEN}3{NC}) Wait for Device (BROM mode entry)")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {GREEN}4{NC}) Backup Partitions")
    print(f"  {GREEN}5{NC}) Flash Single Partition")
    print(f"  {GREEN}6{NC}) Flash Full ROM (Scatter File)")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {YELLOW}{BOLD}  PARTITION TABLE REPAIR{NC}")
    print(f"  {GREEN}a{NC}) Print Partition Table (GPT)")
    print(f"  {GREEN}b{NC}) Backup Partition Table (GPT)")
    print(f"  {GREEN}c{NC}) Restore Partition Table (from backup)")
    print(f"  {GREEN}d{NC}) Rebuild Partition Table (from scatter)")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {GREEN}7{NC}) Erase FRP (Factory Reset Protection)")
    print(f"  {GREEN}8{NC}) Reset NVRAM / NVCFG")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {YELLOW}{BOLD}  QUICK REPAIRS / TOOLS{NC}")
    print(f"  {GREEN}u{NC}) Unlock Bootloader (BROM bypass)")
    print(f"  {GREEN}x{NC}) Fix Bootloop (Wipe Userdata/Cache/Metadata)")
    print(f"  {GREEN}r{NC}) Flash Custom Recovery (TWRP/OrangeFox)")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {RED}{BOLD}  f) ★ FULL UNBRICK (Guided 7-Phase Sequence) ★{NC}")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {YELLOW}{BOLD}  POST-RECOVERY TOOLS{NC}")
    print(f"  {GREEN}t{NC}) ADB & Fastboot Tools (Network / USB)")
    print(f"  {CYAN}{'─' * w}{NC}")
    print(f"  {GREEN}9{NC}) Check mtkclient Installation")
    print(f"  {GREEN}h{NC}) How to Enter BROM Mode (Guide)")
    print(f"  {GREEN}0{NC}) Exit")
    print(f"  {CYAN}{'─' * w}{NC}")
    print()


def brom_guide():
    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  HOW TO ENTER BROM MODE - {DEVICE_NAME}{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"""
  {BOLD}What is BROM mode?{NC}
  Boot ROM (BROM) mode is a low-level recovery mode built into
  the MediaTek {DEVICE_CHIPSET} chipset. It activates when the
  phone cannot find a valid bootloader. This is how we unbrick.

  {BOLD}Steps:{NC}

  {GREEN}1.{NC} Make sure the bricked {DEVICE_NAME} is completely OFF.
     (If it's stuck in a bootloop, hold Power for 15+ seconds
     to force it off.)

  {GREEN}2.{NC} Connect a USB OTG adapter to your host phone (this one).

  {GREEN}3.{NC} On the bricked phone, press and HOLD {BOLD}Volume UP{NC}.

  {GREEN}4.{NC} While holding Vol↑, connect the USB cable from the OTG
     adapter to the bricked phone's USB-C / Micro-USB port.

  {GREEN}5.{NC} Keep holding Vol↑ for about 5-10 seconds.

  {GREEN}6.{NC} On this phone, an Android popup should appear asking
     to grant Termux USB permission. Tap {BOLD}OK{NC}.

  {GREEN}7.{NC} The bricked phone should now appear as:
     {BOLD}MediaTek Inc.  VID: 0E8D  PID: 0003{NC}  (BROM mode)
     or
     {BOLD}MediaTek Inc.  VID: 0E8D  PID: 2000{NC}  (Preloader mode)

  {YELLOW}Troubleshooting:{NC}
  • If the phone doesn't show up, try a different USB cable.
  • Some cables are charge-only and don't carry data.
  • If the battery is completely drained, plug it in to a
    charger for 5 minutes first, then try again.
  • Some phones need Volume DOWN instead. Try both.
  • Try the "short test point" method as a last resort
    (search XDA for "{DEVICE_CODENAME} BROM test point").
""")
    print(f"{CYAN}{'═' * 50}{NC}\n")


def cmd_detect_host():
    info = get_host_info()
    print_host_info(info)


def cmd_scan_device():
    result = smart_scan_usb()
    if not result:
        return None
        
    mode = result.get("mode")
    if mode in ("adb", "fastboot", "recovery"):
        print(f"  {YELLOW}[!] Notice: Device is in {mode.upper()} mode.{NC}")
        ans = input(f"  {YELLOW}Jump to ADB & Fastboot Tools Menu? (Y/n): {NC}").strip().lower()
        if ans != 'n':
            adb_menu()
        return result
        
    return result


def cmd_wait_device():
    try:
        timeout = input(f"  {YELLOW}Timeout in seconds (default 60): {NC}").strip()
        timeout = int(timeout) if timeout else 60
    except ValueError:
        timeout = 60
    return wait_for_device(timeout=timeout)


def cmd_backup(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    output_dir = input(f"  {YELLOW}Backup directory (default ~/unbego_backup): {NC}").strip()
    if not output_dir:
        output_dir = "~/unbego_backup"
    backup_partitions(device_path, output_dir)


def cmd_flash_partition(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    part = input(f"  {YELLOW}Partition name (e.g., boot, recovery, lk, preloader): {NC}").strip()
    if not part:
        print(f"  {RED}[✗] No partition name provided.{NC}")
        return
    image = input(f"  {YELLOW}Image file path (e.g., /sdcard/boot.img): {NC}").strip()
    if not image:
        print(f"  {RED}[✗] No image file provided.{NC}")
        return
    flash_partition(device_path, part, image)


def cmd_flash_custom_recovery(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    image = input(f"  {YELLOW}Recovery Image file path (e.g., TWRP.img): {NC}").strip()
    if not image:
        print(f"  {RED}[✗] No image file provided.{NC}")
        return
    flash_partition(device_path, "recovery", image)


def cmd_flash_scatter(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    scatter = input(f"  {YELLOW}Scatter file path: {NC}").strip()
    if not scatter:
        print(f"  {RED}[✗] No scatter file provided.{NC}")
        return
    flash_scatter(device_path, scatter)


def cmd_print_gpt(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    print_gpt(device_path)


def cmd_backup_gpt(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    output_dir = input(f"  {YELLOW}Backup directory (default ~/unbego_backup): {NC}").strip()
    if not output_dir:
        output_dir = "~/unbego_backup"
    backup_gpt(device_path, output_dir)


def cmd_restore_gpt(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    gpt_file = input(f"  {YELLOW}GPT backup file (e.g., ~/unbego_backup/gpt_main.bin): {NC}").strip()
    if not gpt_file:
        print(f"  {RED}[✗] No GPT file provided.{NC}")
        return
    gpt_file = os.path.expanduser(gpt_file)

    print(f"  {RED}[!] WARNING: Writing the wrong GPT will make things worse.{NC}")
    print(f"  {RED}    Make sure this backup is from the same device or identical model.{NC}")
    confirm = input(f"  {YELLOW}Type 'RESTORE' to confirm: {NC}").strip()
    if confirm != "RESTORE":
        print(f"  {YELLOW}[*] Cancelled.{NC}")
        return
    restore_gpt(device_path, gpt_file)


def cmd_rebuild_gpt(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    scatter = input(f"  {YELLOW}Scatter file path (from stock ROM): {NC}").strip()
    if not scatter:
        print(f"  {RED}[✗] No scatter file provided.{NC}")
        return

    print(f"  {RED}[!] DANGER: This will completely rewrite the partition table.{NC}")
    print(f"  {RED}    All existing data will be inaccessible until each partition is re-flashed.{NC}")
    print(f"  {RED}    This is the nuclear option — use only when the GPT is completely gone.{NC}")
    confirm = input(f"  {YELLOW}Type 'REBUILD' to confirm: {NC}").strip()
    if confirm != "REBUILD":
        print(f"  {YELLOW}[*] Cancelled.{NC}")
        return
    rebuild_gpt_from_scatter(device_path, scatter)


def cmd_erase_frp(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return

    print(f"  {RED}[!] WARNING: This will erase Factory Reset Protection.{NC}")
    confirm = input(f"  {YELLOW}Are you sure? (yes/no): {NC}").strip().lower()
    if confirm != "yes":
        print(f"  {YELLOW}[*] Cancelled.{NC}")
        return
    erase_frp(device_path)


def cmd_reset_nvram(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return

    print(f"  {RED}[!] WARNING: This will erase NVRAM and NVCFG partitions.{NC}")
    print(f"  {RED}    Your IMEI and baseband calibration data will be lost.{NC}")
    print(f"  {RED}    Only proceed if you have a backup or know how to write IMEI.{NC}")
    confirm = input(f"  {YELLOW}Type 'ERASE' to confirm: {NC}").strip()
    if confirm != "ERASE":
        print(f"  {YELLOW}[*] Cancelled.{NC}")
        return
    reset_nvram(device_path)


def cmd_unlock_bootloader(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return
    unlock_bootloader(device_path)


def cmd_quick_fix_boot(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return

    print(f"  {RED}[!] WARNING: This will factory reset the device.{NC}")
    print(f"  {RED}    All photos, apps, and user data will be wiped.{NC}")
    confirm = input(f"  {YELLOW}Type 'WIPE' to confirm: {NC}").strip()
    if confirm != "WIPE":
        print(f"  {YELLOW}[*] Cancelled.{NC}")
        return
    quick_fix_boot(device_path)


def cmd_full_unbrick(device_path=None):
    if not check_mtkclient():
        return
    if not device_path:
        device_path = input(f"  {YELLOW}Device path (e.g., /dev/bus/usb/001/002): {NC}").strip()
    if not device_path:
        print(f"  {RED}[✗] No device path provided.{NC}")
        return

    print(f"\n  {BOLD}★ FULL UNBRICK — Redmi Note 8 Pro ★{NC}")
    print(f"  {YELLOW}This runs all 7 phases automatically:{NC}")
    print(f"  {GREEN}1.{NC} Backup IMEI/calibration  {GREEN}2.{NC} Unlock bootloader")
    print(f"  {GREEN}3.{NC} Flash boot firmware       {GREEN}4.{NC} Flash kernel/recovery")
    print(f"  {GREEN}5.{NC} Flash OS (super/system)   {GREEN}6.{NC} Skip preloader (safe)")
    print(f"  {GREEN}7.{NC} Reboot device")
    print()
    print(f"  {YELLOW}You need the extracted Fastboot ROM (.tgz) images folder.{NC}")
    print(f"  {YELLOW}Download from: https://xiaomifirmwareupdater.com/miui/begonia/{NC}")
    print()

    firmware_dir = input(f"  {YELLOW}Path to extracted firmware images folder: {NC}").strip()
    if not firmware_dir:
        print(f"  {RED}[✗] No firmware directory provided.{NC}")
        return
    firmware_dir = os.path.expanduser(firmware_dir)

    print(f"\n  {RED}[!] WARNING: This will factory reset the bricked phone.{NC}")
    print(f"  {RED}    IMEI/calibration will be backed up automatically.{NC}")
    confirm = input(f"  {YELLOW}Type 'UNBRICK' to proceed: {NC}").strip()
    if confirm != "UNBRICK":
        print(f"  {YELLOW}[*] Cancelled.{NC}")
        return

    full_unbrick(device_path, firmware_dir)


def main():
    banner()

    # Quick host check on startup
    print(f"  {DIM}Detecting host phone...{NC}")
    host = get_host_info()
    host_name = f"{host.get('brand', '?')} {host.get('model', '?')}".title()
    print(f"  {GREEN}Host:{NC} {host_name} | Android {host.get('android_version', '?')} | {host.get('platform', '?')}")
    print(f"  {GREEN}Root:{NC} {'Yes' if host.get('rooted') else 'No (using termux-usb for permissions)'}")
    print()

    # Track last known device path
    last_device_path = None

    while True:
        menu()
        try:
            choice = input(f"  {MAGENTA}unbego ▶ {NC}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {YELLOW}Goodbye!{NC}\n")
            sys.exit(0)

        if choice == "1":
            cmd_detect_host()

        elif choice == "2":
            result = cmd_scan_device()
            if result:
                last_device_path = result.get("path")

        elif choice == "3":
            result = cmd_wait_device()
            if result:
                last_device_path = result.get("path")

        elif choice == "4":
            cmd_backup(last_device_path)

        elif choice == "5":
            cmd_flash_partition(last_device_path)

        elif choice == "6":
            cmd_flash_scatter(last_device_path)

        elif choice == "a":
            cmd_print_gpt(last_device_path)

        elif choice == "b":
            cmd_backup_gpt(last_device_path)

        elif choice == "c":
            cmd_restore_gpt(last_device_path)

        elif choice == "d":
            cmd_rebuild_gpt(last_device_path)

        elif choice == "7":
            cmd_erase_frp(last_device_path)

        elif choice == "8":
            cmd_reset_nvram(last_device_path)

        elif choice == "u":
            cmd_unlock_bootloader(last_device_path)

        elif choice == "x":
            cmd_quick_fix_boot(last_device_path)

        elif choice == "r":
            cmd_flash_custom_recovery(last_device_path)

        elif choice == "f":
            cmd_full_unbrick(last_device_path)

        elif choice == "t":
            adb_menu()

        elif choice == "9":
            if check_mtkclient():
                print(f"  {GREEN}[✓] mtkclient is installed and ready.{NC}\n")
            else:
                print(f"  {RED}[✗] mtkclient not installed. Run ./setup-unbego.sh{NC}\n")

        elif choice == "h":
            brom_guide()

        elif choice in ("0", "q", "exit", "quit"):
            print(f"\n  {YELLOW}Goodbye!{NC}\n")
            sys.exit(0)

        else:
            print(f"  {RED}Invalid option. Try again.{NC}\n")


if __name__ == "__main__":
    # Handle direct CLI commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "host":
            banner()
            cmd_detect_host()
        elif cmd == "scan":
            banner()
            cmd_scan_device()
        elif cmd == "wait":
            banner()
            timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            wait_for_device(timeout)
        elif cmd == "guide":
            banner()
            brom_guide()
        elif cmd == "check":
            banner()
            check_mtkclient()
        elif cmd in ("help", "--help", "-h"):
            banner()
            print(f"  {BOLD}Usage:{NC} unbego [command]")
            print(f"  {DIM}Run without arguments for interactive mode.{NC}\n")
            print(f"  {BOLD}Commands:{NC}")
            print(f"    {GREEN}host{NC}            Show host phone info")
            print(f"    {GREEN}scan{NC}            Scan for bricked device")
            print(f"    {GREEN}wait [timeout]{NC}  Wait for BROM mode device")
            print(f"    {GREEN}guide{NC}           How to enter BROM mode")
            print(f"    {GREEN}check{NC}           Verify mtkclient installation")
            print(f"    {GREEN}help{NC}            Show this help")
            print()
        else:
            print(f"  {RED}Unknown command: {cmd}{NC}")
            print(f"  Run {BOLD}unbego help{NC} for usage.\n")
    else:
        main()
