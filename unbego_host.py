#!/usr/bin/env python3
"""
unbego_host.py - Host Phone Detection Module
Detects the Android phone that is running Termux (the host device).
"""

import subprocess
import os
import json


def run_cmd(cmd):
    """Run a shell command and return stripped output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_host_info():
    """Gather comprehensive info about the host Android phone."""
    info = {}

    # Device model & manufacturer
    info["manufacturer"] = run_cmd("getprop ro.product.manufacturer")
    info["model"] = run_cmd("getprop ro.product.model")
    info["device"] = run_cmd("getprop ro.product.device")
    info["brand"] = run_cmd("getprop ro.product.brand")
    info["name"] = run_cmd("getprop ro.product.name")

    # Android version
    info["android_version"] = run_cmd("getprop ro.build.version.release")
    info["sdk_version"] = run_cmd("getprop ro.build.version.sdk")
    info["security_patch"] = run_cmd("getprop ro.build.version.security_patch")

    # Build info
    info["build_display"] = run_cmd("getprop ro.build.display.id")
    info["build_fingerprint"] = run_cmd("getprop ro.build.fingerprint")

    # Hardware
    info["chipset"] = run_cmd("getprop ro.hardware")
    info["board"] = run_cmd("getprop ro.product.board")
    info["platform"] = run_cmd("getprop ro.board.platform")
    info["cpu_abi"] = run_cmd("getprop ro.product.cpu.abi")

    # Kernel
    info["kernel"] = run_cmd("uname -r")

    # Root status
    info["rooted"] = os.path.exists("/system/xbin/su") or os.path.exists("/system/bin/su") or os.path.exists("/sbin/su")

    # USB OTG support check
    info["usb_otg_supported"] = os.path.exists("/sys/class/typec") or os.path.exists("/sys/class/power_supply/otg_default")

    # Termux:API telephony info (optional, may fail)
    try:
        tel_raw = run_cmd("termux-telephony-deviceinfo")
        if tel_raw:
            tel = json.loads(tel_raw)
            info["imei_sv"] = tel.get("device_software_version", "")
            info["phone_type"] = tel.get("phone_type", "")
            info["network_type"] = tel.get("network_type", "")
    except Exception:
        pass

    return info


def print_host_info(info):
    """Pretty-print host phone information."""
    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BOLD = "\033[1m"
    NC = "\033[0m"

    print(f"\n{CYAN}{'═' * 50}{NC}")
    print(f"{BOLD}  HOST DEVICE INFORMATION{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")

    display_name = f"{info.get('brand', '?')} {info.get('model', '?')}".title()
    print(f"  {GREEN}Device:{NC}         {display_name}")
    print(f"  {GREEN}Manufacturer:{NC}   {info.get('manufacturer', '?')}")
    print(f"  {GREEN}Codename:{NC}       {info.get('device', '?')}")
    print(f"  {GREEN}Android:{NC}        {info.get('android_version', '?')} (SDK {info.get('sdk_version', '?')})")
    print(f"  {GREEN}Security:{NC}       {info.get('security_patch', '?')}")
    print(f"  {GREEN}Chipset:{NC}        {info.get('platform', info.get('chipset', '?'))}")
    print(f"  {GREEN}CPU ABI:{NC}        {info.get('cpu_abi', '?')}")
    print(f"  {GREEN}Kernel:{NC}         {info.get('kernel', '?')}")
    print(f"  {GREEN}Build:{NC}          {info.get('build_display', '?')}")
    print(f"  {GREEN}Rooted:{NC}         {'Yes' if info.get('rooted') else 'No'}")
    print(f"  {GREEN}USB OTG:{NC}        {'Likely Supported' if info.get('usb_otg_supported') else 'Unknown'}")
    print(f"{CYAN}{'═' * 50}{NC}\n")


if __name__ == "__main__":
    info = get_host_info()
    print_host_info(info)
