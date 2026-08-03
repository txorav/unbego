#!/usr/bin/env python3
"""
unbego_detect.py - USB Device Detection Module
Detects bricked Redmi Note 8 Pro in MediaTek BROM / Preloader mode via USB OTG.
Also intelligently detects ADB and Fastboot modes.
"""

import subprocess
import json
import sys
import time
import shutil
import os

# MediaTek USB identifiers
MTK_VENDOR_ID = "0e8d"
XIAOMI_VENDOR_ID = "2717"
GOOGLE_VENDOR_ID = "18d1"

# Known MediaTek mode USB Product IDs
MTK_MODES = {
    "0003": "BROM (Boot ROM) Mode",
    "2000": "Preloader Mode",
    "2001": "CDC Serial (Preloader DA)",
    "20ff": "ADB Composite (Normal Boot)",
}

# Redmi Note 8 Pro specifics
DEVICE_NAME = "Redmi Note 8 Pro"
DEVICE_CODENAME = "begonia"
DEVICE_CHIPSET = "MT6785 (Helio G90T)"

def get_term_width():
    return min(shutil.get_terminal_size((50, 20)).columns, 70)

def request_usb_permissions():
    """Request permission for all connected USB devices via Termux API."""
    if not shutil.which("termux-usb"):
        return
    try:
        out = subprocess.check_output(["termux-usb", "-l"], stderr=subprocess.STDOUT).decode("utf-8")
        devices = [line.strip() for line in out.split('\n') if line.strip().startswith('/dev/')]
        for dev in devices:
            subprocess.run(["termux-usb", "-r", dev], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def get_lsusb_devices():
    """Parse lsusb output for device info."""
    devices = []
    try:
        result = subprocess.run(
            ["lsusb"], capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 6 and "ID" in parts:
                idx = parts.index("ID")
                if idx + 1 < len(parts):
                    vid_pid = parts[idx + 1]
                    desc = " ".join(parts[idx + 2:]) if idx + 2 < len(parts) else ""
                    bus = parts[1] if len(parts) > 1 else "?"
                    dev = parts[3].rstrip(":") if len(parts) > 3 else "?"
                    devices.append({
                        "vid_pid": vid_pid,
                        "bus": bus,
                        "device": dev,
                        "description": desc,
                        "path": f"/dev/bus/usb/{bus}/{dev}",
                    })
    except Exception:
        pass
    return devices

def get_adb_fastboot_cmd(cmd_type="adb"):
    if cmd_type == "adb":
        if shutil.which("termux-adb"): return "termux-adb"
        if shutil.which("adb"): return "adb"
    elif cmd_type == "fastboot":
        if shutil.which("termux-fastboot"): return "termux-fastboot"
        if shutil.which("fastboot"): return "fastboot"
    return None

def smart_scan_usb():
    """Smart scan that automatically requests permissions and determines exact device mode."""
    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    NC = "\033[0m"
    w = get_term_width()

    print(f"\n{CYAN}{'═' * w}{NC}")
    print(f"{BOLD}  SMART USB SCANNER{NC}")
    print(f"{CYAN}{'═' * w}{NC}")
    
    print(f"  {DIM}Requesting USB permissions...{NC}")
    request_usb_permissions()
    # Give termux-usb a moment to settle
    time.sleep(1)
    
    lsusb_devices = get_lsusb_devices()
    if not lsusb_devices:
        print(f"  {YELLOW}No USB devices found.{NC}")
        print(f"  {YELLOW}Tips:{NC}")
        print(f"  • Ensure phone is connected via USB OTG.")
        print(f"  • Try unplugging and re-plugging the USB cable.")
        print(f"{CYAN}{'═' * w}{NC}\n")
        return None

    # Step 1: Check BROM / MediaTek
    for dev in lsusb_devices:
        vid_pid = dev["vid_pid"]
        vid, pid = vid_pid.split(":") if ":" in vid_pid else ("", "")
        
        if vid.lower() == MTK_VENDOR_ID:
            mode = MTK_MODES.get(pid.lower(), f"Unknown MTK mode (PID: {pid})")
            print(f"  {GREEN}[✓] MediaTek Device Detected!{NC}")
            print(f"  {GREEN}Mode:{NC} {mode}")
            print(f"  {GREEN}Path:{NC} {dev['path']}")
            print(f"{CYAN}{'═' * w}{NC}\n")
            return {"mode": "brom", "path": dev["path"], "info": {"chipset": DEVICE_CHIPSET}}
            
    # Step 2: Check ADB
    adb_cmd = get_adb_fastboot_cmd("adb")
    if adb_cmd:
        try:
            out = subprocess.check_output([adb_cmd, "devices"], text=True, timeout=5)
            lines = out.strip().split('\n')
            for line in lines[1:]: # Skip "List of devices attached"
                if "device" in line or "recovery" in line:
                    parts = line.split()
                    state = parts[1]
                    print(f"  {GREEN}[✓] ADB Device Detected! ({state.upper()}){NC}")
                    
                    # Fetch info
                    model = "Unknown"
                    codename = "Unknown"
                    android = "Unknown"
                    if state == "device":
                        try:
                            model = subprocess.check_output([adb_cmd, "-s", parts[0], "shell", "getprop", "ro.product.model"], text=True, timeout=2).strip()
                            codename = subprocess.check_output([adb_cmd, "-s", parts[0], "shell", "getprop", "ro.product.device"], text=True, timeout=2).strip()
                            android = subprocess.check_output([adb_cmd, "-s", parts[0], "shell", "getprop", "ro.build.version.release"], text=True, timeout=2).strip()
                        except: pass
                        
                    print(f"  {GREEN}Model:{NC}   {model} ({codename})")
                    print(f"  {GREEN}Android:{NC} {android}")
                    print(f"{CYAN}{'═' * w}{NC}\n")
                    return {"mode": "adb" if state == "device" else "recovery", "path": parts[0], "info": {"model": model, "codename": codename, "android": android}}
        except Exception:
            pass

    # Step 3: Check Fastboot
    fb_cmd = get_adb_fastboot_cmd("fastboot")
    if fb_cmd:
        try:
            out = subprocess.check_output([fb_cmd, "devices"], text=True, timeout=5)
            if out.strip():
                parts = out.strip().split('\n')[0].split()
                print(f"  {GREEN}[✓] Fastboot Device Detected!{NC}")
                
                codename = "Unknown"
                try:
                    var_out = subprocess.check_output([fb_cmd, "-s", parts[0], "getvar", "product"], stderr=subprocess.STDOUT, text=True, timeout=2)
                    for line in var_out.split('\n'):
                        if "product:" in line:
                            codename = line.split("product:")[1].strip()
                except: pass
                
                print(f"  {GREEN}Codename:{NC} {codename}")
                print(f"{CYAN}{'═' * w}{NC}\n")
                return {"mode": "fastboot", "path": parts[0], "info": {"codename": codename}}
        except Exception:
            pass

    # No specific mode matched but device is plugged in
    print(f"  {YELLOW}[!] USB device detected, but not recognized as ADB, Fastboot, or BROM.{NC}")
    for dev in lsusb_devices:
        print(f"  {YELLOW}Unknown:{NC} {dev['vid_pid']} - {dev['description']}")
    print(f"{CYAN}{'═' * w}{NC}\n")
    return None

def detect_mtk_device():
    # Legacy wrapper for old behavior just in case
    return smart_scan_usb()

def wait_for_device(timeout=60):
    """Poll for MTK device with a countdown (for BROM mode entry)."""
    CYAN = "\033[0;36m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    BOLD = "\033[1m"
    NC = "\033[0m"

    print(f"\n{YELLOW}[*] Waiting for {DEVICE_NAME} in BROM mode...{NC}")
    print(f"    1. Make sure the bricked phone is POWERED OFF.")
    print(f"    2. Hold the Volume UP button on the bricked phone.")
    print(f"    3. While holding Vol↑, connect it to THIS phone via USB OTG.")
    print(f"    4. Keep holding Vol↑ for ~5 seconds after connecting.")
    print(f"    {BOLD}Timeout: {timeout}s{NC}\n")

    for i in range(timeout):
        sys.stdout.write(f"\r  Scanning... ({i + 1}/{timeout}s) ")
        sys.stdout.flush()

        lsusb_devices = get_lsusb_devices()
        for dev in lsusb_devices:
            vid_pid = dev["vid_pid"]
            vid, pid = vid_pid.split(":") if ":" in vid_pid else ("", "")
            if vid.lower() == MTK_VENDOR_ID and pid.lower() in ("0003", "2000"):
                print(f"\r  {GREEN}[✓] MediaTek BROM device detected!{NC}                    ")
                return {
                    "vid": vid, "pid": pid,
                    "mode": MTK_MODES.get(pid.lower(), "Unknown"),
                    "path": dev["path"],
                    "description": dev["description"],
                }
        time.sleep(1)

    print(f"\r  {YELLOW}[!] Timeout reached. No device found.{NC}                    ")
    return None

if __name__ == "__main__":
    smart_scan_usb()
