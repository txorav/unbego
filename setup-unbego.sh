#!/bin/bash
# unbego - Setup script for Termux
# Installs all dependencies needed for unbricking Redmi Note 8 Pro

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

banner() {
    echo -e "${CYAN}"
    echo "  ██╗   ██╗███╗   ██╗██████╗ ███████╗ ██████╗  ██████╗ "
    echo "  ██║   ██║████╗  ██║██╔══██╗██╔════╝██╔════╝ ██╔═══██╗"
    echo "  ██║   ██║██╔██╗ ██║██████╔╝█████╗  ██║  ███╗██║   ██║"
    echo "  ██║   ██║██║╚██╗██║██╔══██╗██╔══╝  ██║   ██║██║   ██║"
    echo "  ╚██████╔╝██║ ╚████║██████╔╝███████╗╚██████╔╝╚██████╔╝"
    echo "   ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝ "
    echo -e "${NC}"
    echo -e "${BOLD}  Redmi Note 8 Pro Unbrick Tool for Termux${NC}"
    echo -e "  MediaTek MT6785 (Helio G90T) Recovery"
    echo ""
}

banner

echo -e "${YELLOW}[*] Updating package lists...${NC}"
pkg update -y

echo -e "${YELLOW}[*] Enabling root-repo and x11-repo (required for usbutils on some Termux versions)...${NC}"
pkg install -y root-repo x11-repo || echo -e "${YELLOW}[!] Could not install extra repos, continuing...${NC}"
pkg update -y

echo -e "${YELLOW}[*] Installing core packages...${NC}"
pkg install -y termux-api usbutils libusb python clang make libffi git android-tools

if ! command -v lsusb &> /dev/null; then
    echo -e "${YELLOW}[!] usbutils not found via pkg. Attempting direct binary download...${NC}"
    curl -sL "https://github.com/termux/termux-root-packages/releases/latest/download/usbutils.deb" -o /tmp/usbutils.deb || \
    curl -sL "https://raw.githubusercontent.com/Magisk-Modules-Repo/usbutils/master/system/bin/lsusb" -o "$PREFIX/bin/lsusb"
    if [ -f "/tmp/usbutils.deb" ]; then
        dpkg -i /tmp/usbutils.deb || echo -e "${RED}[!] dpkg install failed${NC}"
    fi
    chmod +x "$PREFIX/bin/lsusb" 2>/dev/null || true
fi

echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
pip install pyusb pyserial

echo -e "${YELLOW}[*] Cloning mtkclient (MediaTek BROM tool)...${NC}"
MTKCLIENT_DIR="$HOME/mtkclient"
if [ -d "$MTKCLIENT_DIR" ]; then
    echo -e "${GREEN}[+] mtkclient already exists, pulling latest...${NC}"
    cd "$MTKCLIENT_DIR" && git pull
else
    git clone https://github.com/bkerler/mtkclient.git "$MTKCLIENT_DIR"
fi

echo -e "${YELLOW}[*] Installing mtkclient dependencies...${NC}"
cd "$MTKCLIENT_DIR"
pip install -r requirements.txt 2>/dev/null || pip install pycryptodome lxml

echo ""

echo -e "${YELLOW}[*] Installing termux-adb (USB ADB/Fastboot support)...${NC}"
if ! command -v termux-adb &> /dev/null; then
    curl -s https://raw.githubusercontent.com/nohajc/termux-adb/master/install.sh | bash || echo -e "${RED}[!] Failed to install termux-adb${NC}"
else
    echo -e "${GREEN}[+] termux-adb is already installed.${NC}"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}[✓] Setup complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Connect the bricked Redmi Note 8 Pro via USB OTG"
echo -e "  2. Run: ${BOLD}./unbego${NC}"
echo ""
