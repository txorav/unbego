#!/usr/bin/env python3
"""
unbego_adb.py - ADB and Fastboot Tools
Provides interactive ADB/Fastboot functionality for Termux.
Uses termux-adb/termux-fastboot for USB OTG, and native adb for Network.
"""

import os
import subprocess
import shutil
import time

# Use detect module for permissions and width if possible
try:
    from unbego_detect import request_usb_permissions, get_term_width
except ImportError:
    request_usb_permissions = lambda: None
    get_term_width = lambda: 50

# ── Colors ──────────────────────────────────────────────
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
NC = "\033[0m"


def run_interactive(cmd_list):
    """Run a command interactively (connects stdin/stdout)."""
    try:
        subprocess.run(cmd_list)
    except KeyboardInterrupt:
        print(f"\n  {YELLOW}[*] Interrupted.{NC}")
    except Exception as e:
        print(f"  {RED}[!] Error: {e}{NC}")


def get_adb_cmd(use_network=False):
    """Return the base command for adb."""
    if use_network:
        if shutil.which("adb"):
            return "adb"
        return None
    
    # Prefer termux-adb for USB
    if shutil.which("termux-adb"):
        return "termux-adb"
    # Fallback to native
    if shutil.which("adb"):
        return "adb"
    return None


def get_fastboot_cmd():
    """Return the base command for fastboot."""
    if shutil.which("termux-fastboot"):
        return "termux-fastboot"
    if shutil.which("fastboot"):
        return "fastboot"
    return None


def request_usb_permissions():
    """Stub in case import fails"""
    pass

def cmd_list_devices():
    request_usb_permissions()
    print(f"\n  {CYAN}--- USB Devices (termux-adb) ---{NC}")
    cmd = get_adb_cmd(use_network=False)
    if cmd:
        run_interactive([cmd, "devices"])
    else:
        print(f"  {RED}[✗] ADB not found. Run ./setup-unbego.sh{NC}")

    print(f"\n  {CYAN}--- Network Devices (native adb) ---{NC}")
    cmd_net = get_adb_cmd(use_network=True)
    if cmd_net:
        run_interactive([cmd_net, "devices"])
        
    print(f"\n  {CYAN}--- Fastboot Devices ---{NC}")
    fb_cmd = get_fastboot_cmd()
    if fb_cmd:
        run_interactive([fb_cmd, "devices"])


def cmd_network_connect():
    ip = input(f"\n  {YELLOW}Enter device IP address (e.g., 192.168.1.50): {NC}").strip()
    if not ip:
        return
    port = input(f"  {YELLOW}Enter port (leave blank for 5555): {NC}").strip()
    if not port:
        port = "5555"
        
    cmd = get_adb_cmd(use_network=True)
    if not cmd:
        print(f"  {RED}[✗] Native ADB not found. Run ./setup-unbego.sh{NC}")
        return
        
    print(f"  {CYAN}[*] Connecting to {ip}:{port}...{NC}")
    run_interactive([cmd, "connect", f"{ip}:{port}"])


def cmd_interactive_shell():
    print(f"\n  {YELLOW}[*] Opening interactive ADB Shell. Type 'exit' to return.{NC}")
    cmd = get_adb_cmd(use_network=False)
    if not cmd:
        return
    run_interactive([cmd, "shell"])


def cmd_sideload():
    print(f"\n  {YELLOW}[*] Ensure the device is in Recovery mode and 'Apply update from ADB' is selected.{NC}")
    filepath = input(f"  {YELLOW}Path to OTA .zip file: {NC}").strip()
    if not filepath or not os.path.isfile(filepath):
        print(f"  {RED}[✗] File not found.{NC}")
        return
        
    cmd = get_adb_cmd(use_network=False)
    if not cmd:
        return
    print(f"  {CYAN}[*] Sideloading {filepath}... This will take a while.{NC}")
    run_interactive([cmd, "sideload", filepath])


def cmd_reboot():
    print(f"\n  {CYAN}Reboot Options:{NC}")
    print(f"  1) System (Normal)")
    print(f"  2) Recovery")
    print(f"  3) Fastboot / Bootloader")
    print(f"  4) EDL / BROM (Emergency Download)")
    print(f"  5) Fastboot Reboot (if currently in fastboot)")
    
    choice = input(f"\n  {YELLOW}Select reboot mode: {NC}").strip()
    
    adb_cmd = get_adb_cmd(use_network=False)
    fb_cmd = get_fastboot_cmd()
    
    if choice == "1":
        run_interactive([adb_cmd, "reboot"])
    elif choice == "2":
        run_interactive([adb_cmd, "reboot", "recovery"])
    elif choice == "3":
        run_interactive([adb_cmd, "reboot", "bootloader"])
    elif choice == "4":
        run_interactive([adb_cmd, "reboot", "edl"])
    elif choice == "5":
        if fb_cmd:
            run_interactive([fb_cmd, "reboot"])
        else:
            print(f"  {RED}[✗] Fastboot not found.{NC}")
    else:
        print(f"  {RED}[✗] Invalid option.{NC}")


def cmd_fastboot_flash():
    print(f"\n  {YELLOW}[*] Ensure the device is in Fastboot mode.{NC}")
    partition = input(f"  {YELLOW}Partition to flash (e.g., boot, recovery, system): {NC}").strip()
    if not partition:
        return
    filepath = input(f"  {YELLOW}Path to image file (.img): {NC}").strip()
    if not filepath or not os.path.isfile(filepath):
        print(f"  {RED}[✗] File not found.{NC}")
        return
        
    fb_cmd = get_fastboot_cmd()
    if not fb_cmd:
        print(f"  {RED}[✗] Fastboot not found.{NC}")
        return
        
    print(f"  {CYAN}[*] Flashing {filepath} to {partition}...{NC}")
    run_interactive([fb_cmd, "flash", partition, filepath])


def cmd_wait_for_device():
    print(f"\n  {YELLOW}[*] Waiting for device to be connected and authorized...{NC}")
    print(f"  {YELLOW}    (Press Ctrl+C to cancel){NC}")
    cmd = get_adb_cmd(use_network=False)
    if not cmd:
        return
    run_interactive([cmd, "wait-for-device"])
    print(f"  {GREEN}[✓] Device detected!{NC}")


def adb_menu():
    w = get_term_width()
    while True:
        print(f"\n  {CYAN}{'─' * w}{NC}")
        print(f"  {BOLD}ADB & FASTBOOT TOOLS{NC}")
        print(f"  {CYAN}{'─' * w}{NC}")
        print(f"  {GREEN}1{NC}) List Devices (ADB & Fastboot)")
        print(f"  {GREEN}2{NC}) Connect to Network ADB (Wireless)")
        print(f"  {GREEN}3{NC}) Open ADB Shell")
        print(f"  {GREEN}4{NC}) ADB Sideload (OTA Zip)")
        print(f"  {GREEN}5{NC}) Reboot Device (ADB / Fastboot)")
        print(f"  {GREEN}6{NC}) Fastboot Flash Image")
        print(f"  {GREEN}7{NC}) Wait for Device")
        print(f"  {CYAN}{'─' * w}{NC}")
        print(f"  {GREEN}0{NC}) Back to Main Menu")
        print(f"  {CYAN}{'─' * w}{NC}")

        choice = input(f"  {YELLOW}Select an option: {NC}").strip()

        if choice == "1":
            cmd_list_devices()
        elif choice == "2":
            cmd_network_connect()
        elif choice == "3":
            cmd_interactive_shell()
        elif choice == "4":
            cmd_sideload()
        elif choice == "5":
            cmd_reboot()
        elif choice == "6":
            cmd_fastboot_flash()
        elif choice == "7":
            cmd_wait_for_device()
        elif choice in ("0", "q", "exit", "quit"):
            break
        else:
            print(f"  {RED}Invalid option. Try again.{NC}\n")
