# unbego

**Unbrick your Redmi Note 8 Pro from another Android phone using Termux + USB OTG. No root required.**

```
  ██╗   ██╗███╗   ██╗██████╗ ███████╗ ██████╗  ██████╗
  ██║   ██║████╗  ██║██╔══██╗██╔════╝██╔════╝ ██╔═══██╗
  ██║   ██║██╔██╗ ██║██████╔╝█████╗  ██║  ███╗██║   ██║
  ██║   ██║██║╚██╗██║██╔══██╗██╔══╝  ██║   ██║██║   ██║
  ╚██████╔╝██║ ╚████║██████╔╝███████╗╚██████╔╝╚██████╔╝
   ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝
```

## What is this?

`unbego` is a Termux-based tool that lets you unbrick a **Redmi Note 8 Pro** (codename: **begonia**, chipset: **MediaTek MT6785 / Helio G90T**) using **another Android phone** as the host, connected via a USB OTG cable. No PC required. No root required.

It works by communicating with the MediaTek Boot ROM (BROM) mode built into the phone's chipset, using the open-source [mtkclient](https://github.com/bkerler/mtkclient) library.

## Requirements

| Item | Details |
|---|---|
| **Host Phone** | Any Android phone with USB OTG support running Termux |
| **Apps** | [Termux](https://f-droid.org/en/packages/com.termux/) + [Termux:API](https://f-droid.org/en/packages/com.termux.api/) (both from F-Droid) |
| **USB OTG Cable** | USB-C OTG adapter + data cable to the bricked phone |
| **Bricked Phone** | Redmi Note 8 Pro (begonia) |
| **Firmware** | Stock ROM / scatter file for Redmi Note 8 Pro (download separately) |
| **Root** | ❌ NOT required |

## Installation

```bash
# 1. Clone or copy the unbego folder to Termux
# 2. Run the setup script
cd unbego
chmod +x setup-unbego.sh
./setup-unbego.sh
```

This installs: `termux-api`, `libusb`, `usbutils`, `python`, `pyusb`, `pyserial`, and `mtkclient`.

## Usage

### Interactive Mode (Recommended)

```bash
chmod +x unbego
./unbego
```

This launches an interactive menu:

```
  1) Detect Host Phone (this device)
  2) Scan for Bricked Device (USB OTG)
  3) Wait for Device (BROM mode entry)
  4) Backup Partitions
  5) Flash Single Partition
  6) Flash Full ROM (Scatter File)
  7) Erase FRP (Factory Reset Protection)
  8) Reset NVRAM / NVCFG
  9) Check mtkclient Installation
  h) How to Enter BROM Mode (Guide)
  0) Exit
```

### Direct CLI Commands

```bash
./unbego host          # Show host phone info
./unbego scan          # Scan for bricked device on USB
./unbego wait 120      # Wait up to 120s for BROM mode
./unbego guide         # How to enter BROM mode
./unbego check         # Verify mtkclient is installed
./unbego help          # Show all commands
```

## How to Unbrick (Step by Step)

### Step 1: Setup
```bash
./setup-unbego.sh
```

### Step 2: Connect the bricked phone
1. Plug a **USB OTG adapter** into your host phone.
2. Make sure the bricked Redmi Note 8 Pro is **completely powered off**.
3. On the bricked phone, **hold Volume UP**.
4. While holding Vol↑, connect the USB cable from the OTG adapter to the bricked phone.
5. Keep holding Vol↑ for about 5-10 seconds.
6. Android will show a popup asking to grant Termux USB permission — tap **OK**.

### Step 3: Detect the device
```bash
./unbego
# Choose option 2 (Scan) or 3 (Wait for Device)
```

You should see:
```
  [✓] MediaTek device detected!
  VID:PID:    0e8d:0003
  Mode:       BROM (Boot ROM) Mode
```

### Step 4: Backup (Important!)
Before flashing, always backup critical partitions:
```
  Choose option 4 → Backup Partitions
```

### Step 5: Flash firmware
- **Option 5**: Flash a single partition (e.g., `boot`, `recovery`, `preloader`)
- **Option 6**: Flash a full ROM using a scatter file

### Step 6: Reboot
After flashing, disconnect the USB cable and hold Power to boot.

## File Structure

```
unbego/
├── unbego              # Main entry point (bash)
├── unbego_core.py      # Interactive CLI & command dispatcher
├── unbego_host.py      # Host phone detection (getprop, termux-api)
├── unbego_detect.py    # USB device scanning (MediaTek BROM detection)
├── unbego_flash.py     # Flash/backup/erase operations (mtkclient wrapper)
├── setup-unbego.sh     # Dependency installer
└── README.md           # This file
```

## MediaTek USB Identifiers

| PID | Mode | Meaning |
|-----|------|---------|
| `0x0003` | BROM | Boot ROM mode — fully flashable |
| `0x2000` | Preloader | Preloader mode — flashable |
| `0x2001` | CDC Serial | Download Agent active |
| `0x20FF` | ADB | Phone is booted normally |

VID is always `0x0E8D` (MediaTek Inc.)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No device detected | Try a different USB cable (must be data cable, not charge-only) |
| Permission denied | Make sure Termux:API app is installed from F-Droid |
| Phone won't enter BROM | Hold Vol↑ for longer, or try Vol↓. Ensure phone is fully off |
| Dead battery | Charge for 5 min first, then retry BROM entry |
| mtkclient errors | Run `./setup-unbego.sh` again to update |

## Credits

- [mtkclient](https://github.com/bkerler/mtkclient) by bkerler — MediaTek BROM/Preloader protocol implementation
- [Termux](https://termux.dev) — Terminal emulator for Android
- [Termux:API](https://wiki.termux.com/wiki/Termux:API) — Android API access from Termux
