#!/bin/bash
# unbego - Easy Termux Install Script
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/unbego/main/install.sh)

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   UNBEGO — TERMUX INSTALLER              ║"
echo "  ║   Redmi Note 8 Pro (MT6785) Unbrick      ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "  ${YELLOW}[*] Installing required packages (git)...${NC}"
pkg update -y
pkg install -y git curl

INSTALL_DIR="$HOME/unbego"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "  ${YELLOW}[*] Updating existing unbego installation...${NC}"
    cd "$INSTALL_DIR"
    git pull
else
    echo -e "  ${YELLOW}[*] Cloning unbego repository...${NC}"
    # Replace 'YOUR_GITHUB_USERNAME' with the actual username after pushing
    git clone https://github.com/YOUR_GITHUB_USERNAME/unbego.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo -e "  ${YELLOW}[*] Setting execute permissions...${NC}"
chmod +x setup-unbego.sh unbego download-firmware.sh

echo -e "  ${YELLOW}[*] Running unbego setup...${NC}"
./setup-unbego.sh

echo -e "\n${GREEN}${BOLD}  [✓] INSTALLATION COMPLETE!${NC}"
echo -e "  ${YELLOW}To start unbego, run:${NC}"
echo -e "  ${BOLD}cd ~/unbego && ./unbego${NC}"
echo ""
