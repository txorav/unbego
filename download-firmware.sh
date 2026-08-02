#!/bin/bash
# unbego firmware downloader
# Downloads ONLY what you need — not the full 3GB+ ROM

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

FIRMWARE_DIR="$HOME/unbego_firmware"
mkdir -p "$FIRMWARE_DIR"

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   UNBEGO FIRMWARE DOWNLOADER             ║"
echo "  ║   Redmi Note 8 Pro (begonia / MT6785)    ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "  ${BOLD}Select your device region:${NC}"
echo -e "  ${GREEN}1${NC}) Global (most common)"
echo -e "  ${GREEN}2${NC}) EEA / Europe"
echo -e "  ${GREEN}3${NC}) India (begoniain — no NFC)"
echo -e "  ${GREEN}4${NC}) China"
echo ""
read -p "  Region [1]: " REGION
REGION=${REGION:-1}

case $REGION in
    1)
        ROM_URL="https://bigota.d.miui.com/V12.5.8.0.RGGMIXM/begonia_global_images_V12.5.8.0.RGGMIXM_20220302.0000.00_11.0_global_8d94e2e2a2.tgz"
        ROM_FILE="begonia_global_V12.5.8.0.RGGMIXM.tgz"
        ROM_VER="V12.5.8.0.RGGMIXM (Global)"
        ;;
    2)
        ROM_URL="https://bigota.d.miui.com/V12.5.7.0.RGGEUXM/begonia_eea_global_images_V12.5.7.0.RGGEUXM_20220317.0000.00_11.0_eea_a0ca01aeb4.tgz"
        ROM_FILE="begonia_eea_V12.5.7.0.RGGEUXM.tgz"
        ROM_VER="V12.5.7.0.RGGEUXM (EEA)"
        ;;
    3)
        ROM_URL="https://bigota.d.miui.com/V12.5.10.0.RGINXM/begonia_in_global_images_V12.5.10.0.RGINXM_20220412.0000.00_11.0_in_42797686ba.tgz"
        ROM_FILE="begonia_in_V12.5.10.0.RGINXM.tgz"
        ROM_VER="V12.5.10.0.RGINXM (India)"
        ;;
    4)
        ROM_URL="https://bigota.d.miui.com/V12.5.15.0.RGGCNXM/begonia_images_V12.5.15.0.RGGCNXM_20220309.0000.00_11.0_cn_50567f2b1d.tgz"
        ROM_FILE="begonia_cn_V12.5.15.0.RGGCNXM.tgz"
        ROM_VER="V12.5.15.0.RGGCNXM (China)"
        ;;
    *)
        echo -e "  ${RED}Invalid selection.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "  ${BOLD}What do you need?${NC}"
echo ""
echo -e "  ${GREEN}1${NC}) ${BOLD}Scatter file only${NC} (~50 KB)"
echo -e "     ${DIM}Needed for: GPT rebuild, partition mapping${NC}"
echo ""
echo -e "  ${GREEN}2${NC}) ${BOLD}Boot essentials only${NC} (~150 MB)"
echo -e "     ${DIM}Includes: preloader, lk, boot, recovery, vbmeta, dtbo, tee, scp${NC}"
echo -e "     ${DIM}Enough to fix: bootloop, corrupted kernel, dead bootloader${NC}"
echo ""
echo -e "  ${GREEN}3${NC}) ${BOLD}Full ROM${NC} (~3+ GB)"
echo -e "     ${DIM}Includes everything: boot + system + vendor + super${NC}"
echo -e "     ${DIM}Needed for: complete unbrick from scratch${NC}"
echo ""
read -p "  Download option [2]: " DL_OPTION
DL_OPTION=${DL_OPTION:-2}

# ── Step 1: Download scatter file (always needed, tiny) ──
SCATTER_URL="https://gist.githubusercontent.com/michaelskyf/eff1894ec531e659f2a2ec393ba61697/raw/MT6785_Android_scatter.txt"
SCATTER_FILE="$FIRMWARE_DIR/MT6785_Android_scatter.txt"

if [ "$DL_OPTION" == "1" ]; then
    echo -e "\n  ${YELLOW}[*] Downloading scatter file...${NC}"
    curl -L -o "$SCATTER_FILE" "$SCATTER_URL" 2>/dev/null || wget -q -O "$SCATTER_FILE" "$SCATTER_URL"
    echo -e "  ${GREEN}[✓] Scatter file saved to: $SCATTER_FILE${NC}"
    echo -e "  ${GREEN}[✓] Size: $(du -h "$SCATTER_FILE" | cut -f1)${NC}"
    echo ""
    echo -e "  ${GREEN}Done! Use this scatter file with unbego options c/d.${NC}"
    exit 0
fi

# ── Step 2: Download the ROM archive ──
echo -e "\n  ${YELLOW}[*] ROM: $ROM_VER${NC}"
echo -e "  ${YELLOW}[*] Downloading from Xiaomi CDN...${NC}"
echo -e "  ${DIM}    URL: $ROM_URL${NC}"
echo -e "  ${YELLOW}[*] This may take a while on mobile data.${NC}"
echo ""

ARCHIVE_PATH="$FIRMWARE_DIR/$ROM_FILE"

if [ -f "$ARCHIVE_PATH" ]; then
    echo -e "  ${GREEN}[✓] Archive already downloaded: $ARCHIVE_PATH${NC}"
else
    curl -L -# -o "$ARCHIVE_PATH" "$ROM_URL" || wget --progress=bar:force -O "$ARCHIVE_PATH" "$ROM_URL"
fi

# ── Step 3: Extract only what we need ──
IMAGES_DIR="$FIRMWARE_DIR/images"
mkdir -p "$IMAGES_DIR"

echo -e "\n  ${YELLOW}[*] Extracting firmware images...${NC}"

if [ "$DL_OPTION" == "2" ]; then
    # Boot essentials only — extract specific small files
    ESSENTIAL_FILES=(
        "preloader_begonia.bin"
        "lk.img"
        "boot.img"
        "recovery.img"
        "vbmeta.img"
        "vbmeta_system.img"
        "vbmeta_vendor.img"
        "dtbo.img"
        "tee.img"
        "scp.img"
        "sspm.img"
        "spmfw.img"
        "md1img.img"
        "logo.img"
        "MT6785_Android_scatter.txt"
    )

    echo -e "  ${YELLOW}[*] Extracting boot essentials only (skipping 3GB+ system images)...${NC}"

    # Build tar extract pattern (files are inside images/ subfolder in the tgz)
    PATTERNS=""
    for f in "${ESSENTIAL_FILES[@]}"; do
        PATTERNS="$PATTERNS --include='*/$f'"
    done

    # Extract with wildcard matching (tgz has nested dirs)
    eval tar xzf "$ARCHIVE_PATH" -C "$FIRMWARE_DIR" --strip-components=1 $PATTERNS 2>/dev/null || \
    eval tar xzf "$ARCHIVE_PATH" -C "$FIRMWARE_DIR" $PATTERNS 2>/dev/null || \
    {
        echo -e "  ${YELLOW}[*] Selective extract failed, extracting all then cleaning...${NC}"
        tar xzf "$ARCHIVE_PATH" -C "$FIRMWARE_DIR" --strip-components=1 2>/dev/null || \
        tar xzf "$ARCHIVE_PATH" -C "$FIRMWARE_DIR"

        # Remove large OS images to save space
        echo -e "  ${YELLOW}[*] Removing large OS images to save space...${NC}"
        find "$FIRMWARE_DIR" -name "super.img" -delete 2>/dev/null
        find "$FIRMWARE_DIR" -name "system.img" -delete 2>/dev/null
        find "$FIRMWARE_DIR" -name "vendor.img" -delete 2>/dev/null
        find "$FIRMWARE_DIR" -name "cust.img" -delete 2>/dev/null
        find "$FIRMWARE_DIR" -name "userdata.img" -delete 2>/dev/null
        find "$FIRMWARE_DIR" -name "cache.img" -delete 2>/dev/null
    }

    # Delete the archive to save space
    echo -e "  ${YELLOW}[*] Deleting ROM archive to free space...${NC}"
    rm -f "$ARCHIVE_PATH"

elif [ "$DL_OPTION" == "3" ]; then
    # Full extraction
    echo -e "  ${YELLOW}[*] Extracting full ROM...${NC}"
    tar xzf "$ARCHIVE_PATH" -C "$FIRMWARE_DIR" --strip-components=1 2>/dev/null || \
    tar xzf "$ARCHIVE_PATH" -C "$FIRMWARE_DIR"

    # Delete archive after extraction
    echo -e "  ${YELLOW}[*] Deleting ROM archive to free space...${NC}"
    rm -f "$ARCHIVE_PATH"
fi

# ── Step 4: Find and report ──
echo ""
echo -e "  ${CYAN}════════════════════════════════════════════${NC}"
echo -e "  ${BOLD}  DOWNLOAD COMPLETE${NC}"
echo -e "  ${CYAN}════════════════════════════════════════════${NC}"

# Try to find the images directory (could be nested)
REAL_IMAGES=$(find "$FIRMWARE_DIR" -name "MT6785_Android_scatter.txt" -printf '%h\n' 2>/dev/null | head -1)
if [ -z "$REAL_IMAGES" ]; then
    REAL_IMAGES=$(find "$FIRMWARE_DIR" -name "boot.img" -printf '%h\n' 2>/dev/null | head -1)
fi
if [ -z "$REAL_IMAGES" ]; then
    REAL_IMAGES="$FIRMWARE_DIR"
fi

echo -e "  ${GREEN}Firmware path:${NC} $REAL_IMAGES"
echo -e "  ${GREEN}Total size:${NC}    $(du -sh "$FIRMWARE_DIR" | cut -f1)"
echo ""

echo -e "  ${GREEN}Files available:${NC}"
ls -lh "$REAL_IMAGES"/*.img "$REAL_IMAGES"/*.bin "$REAL_IMAGES"/*.txt 2>/dev/null | awk '{print "    " $NF " (" $5 ")"}'
echo ""

echo -e "  ${BOLD}Next steps:${NC}"
echo -e "  1. Run ${BOLD}./unbego${NC}"
echo -e "  2. Choose ${BOLD}f${NC} (Full Unbrick)"
echo -e "  3. Enter firmware path: ${BOLD}$REAL_IMAGES${NC}"
echo -e "  ${CYAN}════════════════════════════════════════════${NC}"
echo ""
