#!/usr/bin/env python3
"""
unbego_detect.py - USB Device Detection Module
Detects bricked Redmi Note 8 Pro in MediaTek BROM / Preloader mode via USB OTG.
"""

import subprocess
import json
import sys
import time

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


def get_usb_devices_termux():
    """Get USB devices from termux-usb -l (returns JSON array of device paths)."""
    try:
        result = subprocess.run(
            ["termux-usb", "-l"],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout.strip():
            devices = json.loads(result.stdout.strip())
            return devices if isinstance(devices, list) else []
    except Exception as e:
        print(f"  [!] termux-usb error: {e}")
    return []


def get_lsusb_devices():
    """Parse lsusb output for device info."""
    devices = []
    try:
        result = subprocess.run(
            ["lsusb"], capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().splitlines():
            # Format: Bus 001 Device 002: ID 0e8d:0003 MediaTek Inc. ...
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


def detect_mtk_device():
    """Detect a MediaTek device in BROM or Preloader mode."""
    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BOLD = "\033[1m"
    NC = "\033[0m"

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  USB DEVICE DETECTION{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")

    # Get termux-usb device list
    termux_devices = get_usb_devices_termux()
    print(f"  {GREEN}Termux USB paths:{NC} {termux_devices if termux_devices else 'None detected'}")

    # Get lsusb info
    lsusb_devices = get_lsusb_devices()
    if not lsusb_devices:
        print(f"  {YELLOW}lsusb:{NC} No USB devices found")

    # Search for MediaTek device
    mtk_found = None
    for dev in lsusb_devices:
        vid_pid = dev["vid_pid"]
        vid, pid = vid_pid.split(":") if ":" in vid_pid else ("", "")
        print(f"  {GREEN}Found:{NC} {vid_pid} - {dev['description']} [{dev['path']}]")

        if vid.lower() == MTK_VENDOR_ID:
            mode = MTK_MODES.get(pid.lower(), f"Unknown MTK mode (PID: {pid})")
            mtk_found = {
                "vid": vid,
                "pid": pid,
                "mode": mode,
                "path": dev["path"],
                "description": dev["description"],
            }
        elif vid.lower() in (XIAOMI_VENDOR_ID, GOOGLE_VENDOR_ID):
            print(f"  {YELLOW}[!] Note: Device is in ADB/Fastboot mode, NOT BROM/Preloader.{NC}")
            print(f"  {YELLOW}    -> Use the 'ADB & Fastboot Tools' menu (Option t).{NC}")

    print(f"{CYAN}{'─' * 50}{NC}")

    if mtk_found:
        print(f"  {GREEN}[✓] MediaTek device detected!{NC}")
        print(f"  {GREEN}VID:PID:{NC}    {mtk_found['vid']}:{mtk_found['pid']}")
        print(f"  {GREEN}Mode:{NC}       {mtk_found['mode']}")
        print(f"  {GREEN}Path:{NC}       {mtk_found['path']}")
        print(f"  {GREEN}Target:{NC}     {DEVICE_NAME} ({DEVICE_CODENAME}) - {DEVICE_CHIPSET}")

        if mtk_found["pid"].lower() in ("0003", "2000"):
            print(f"\n  {GREEN}[✓] Device is in flashable mode! Ready for unbrick.{NC}")
        elif mtk_found["pid"].lower() == "20ff":
            print(f"\n  {YELLOW}[!] Device appears to be booted normally (ADB mode).{NC}")
            print(f"  {YELLOW}    It may not be bricked. Power off and hold Vol+ to enter BROM.{NC}")
        print(f"{CYAN}{'═' * 50}{NC}\n")
        return mtk_found
    else:
        print(f"  {RED}[✗] No MediaTek device detected.{NC}")
        print(f"  {YELLOW}Tips:{NC}")
        print(f"  • Ensure the {DEVICE_NAME} is connected via USB OTG cable.")
        print(f"  • The bricked phone should be OFF. Hold Vol↑ + plug USB to enter BROM mode.")
        print(f"  • Try unplugging and re-plugging the USB cable.")
        print(f"  • If the battery is completely dead, hold Vol↑ while plugging in for 10+ seconds.")
        print(f"{CYAN}{'═' * 50}{NC}\n")
        return None


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
    detect_mtk_device()
