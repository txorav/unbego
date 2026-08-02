# Redmi Note 8 Pro (begonia) — Complete Unbrick & Firmware Guide

> **Device:** Redmi Note 8 Pro  
> **Codename:** `begonia` (Global/EU/RU) / `begoniain` (India)  
> **Chipset:** MediaTek MT6785 (Helio G90T)  
> **Storage:** UFS 2.1 (64GB / 128GB)  
> **Partition Scheme:** Non-A/B, Retrofit Dynamic Partitions (Android 10+)

---

## 1. Stock ROM Downloads

> **IMPORTANT:** The Redmi Note 8 Pro reached End-Of-Support on MIUI 12.5 (Android 11). No HyperOS or MIUI 13/14 updates exist.

### Which ROM format do you need?
| Format | Extension | Contains Scatter? | Use For |
|--------|-----------|-------------------|---------|
| **Fastboot ROM** | `.tgz` | ✅ YES | SP Flash Tool, mtkclient, Mi Flash — **USE THIS** |
| Recovery ROM | `.zip` | ❌ NO | MIUI Updater / TWRP only — NOT for unbricking |

### Download Sources

**Xiaomi Firmware Updater (Primary):**
- https://xiaomifirmwareupdater.com/miui/begonia/
- https://xiaomifirmwareupdater.com/archive/miui/begonia/

**MiFirm (Direct Server Links):**
- https://mifirm.net/device/begonia

**XiaomiROM:**
- https://xiaomirom.com/en/rom/redmi-note-8-pro-begonia-global-fastboot-recovery-rom/

### Recommended Versions (Latest Stable Fastboot)

| Region | Version | Filename |
|--------|---------|----------|
| **Global** | V12.5.8.0.RGGMIXM | `begonia_global_images_V12.5.8.0.RGGMIXM_20220302.0000.00_11.0_global_8d94e2e2a2.tgz` |
| **EEA/Europe** | V12.5.7.0.RGGEUXM | `begonia_eea_global_images_V12.5.7.0.RGGEUXM_20220317.0000.00_11.0_eea_a0ca01aeb4.tgz` |
| **India** | V12.5.10.0.RGINXM | `begonia_in_global_images_V12.5.10.0.RGINXM_20220412.0000.00_11.0_in_42797686ba.tgz` |
| **China** | V12.5.15.0.RGGCNXM | `begonia_images_V12.5.15.0.RGGCNXM_20220309.0000.00_11.0_cn_50567f2b1d.tgz` |

### Scatter File Location
After extracting the `.tgz`:
```
<rom_folder>/images/MT6785_Android_scatter.txt
```

**Standalone scatter file (GitHub Gist):**
- https://gist.github.com/michaelskyf/eff1894ec531e659f2a2ec393ba61697

---

## 2. Complete Partition Layout

### Boot & Hardware Firmware
| Partition | Size | Description |
|-----------|------|-------------|
| `preloader` | ~256-512 KB | 1st stage bootloader (UFS LU1/LU2). Inits DRAM & BROM |
| `lk` / `lk2` | ~2-4 MB | Little Kernel (2nd stage bootloader, fastboot) |
| `boot` | ~64 MB | Android kernel + ramdisk |
| `recovery` | ~64 MB | Stock/custom recovery |
| `dtbo` | ~8 MB | Device Tree Blob Overlay |
| `logo` | ~8-16 MB | Boot splash screen |
| `vbmeta` | ~4-8 MB | Android Verified Boot keys |
| `vbmeta_system` | ~4 MB | AVB signature for system |
| `vbmeta_vendor` | ~4 MB | AVB signature for vendor |
| `tee1` / `tee2` | ~5-10 MB | ARM TrustZone OS |
| `scp1` / `scp2` | ~2-4 MB | System Control Processor firmware |
| `sspm_1` / `sspm_2` | ~1-2 MB | System Power Manager firmware |
| `spmfw` | ~1 MB | Power Manager firmware |
| `md1img` | ~50-100 MB | 4G modem/baseband firmware |
| `gz1` / `gz2` | ~10-20 MB | GenieZone (TEE hypervisor) |
| `cam_vpu1/2/3` | ~4-8 MB | Camera Vision Processing Unit firmware |
| `audio_dsp` | ~1-2 MB | Audio DSP firmware |

### ⚠️ CRITICAL — IMEI & Calibration (NEVER OVERWRITE WITHOUT BACKUP)
| Partition | Size | Description |
|-----------|------|-------------|
| `nvram` | ~5 MB | **IMEI 1 & 2**, WiFi MAC, BT MAC, RF calibration |
| `nvdata` | ~32-64 MB | Dynamic NVRAM runtime data |
| `nvcfg` | ~8 MB | NVRAM configuration |
| `proinfo` | ~3 MB | Serial number, hardware revision |
| `protect1` / `protect2` | ~8-16 MB | Factory IMEI backups, network config |
| `persist` | ~32-64 MB | Sensor calibration, DRM (Widevine L1), FRP |
| `seccfg` | ~256 KB | Bootloader lock/unlock flag |
| `sec1` / `secro` | varies | Crypto key storage |

### OS & Storage
| Partition | Size | Description |
|-----------|------|-------------|
| `super` | ~4.5-5.5 GB | Dynamic partition container (Android 10/11) — holds `system`, `vendor`, `product` |
| `system` | ~3-4 GB | Android system (physical on Android 9, inside `super` on 10+) |
| `vendor` | ~1-1.5 GB | Vendor drivers (physical on Android 9, inside `super` on 10+) |
| `cust` | ~800 MB-1 GB | Regional customizations |
| `cache` | ~430 MB | System cache |
| `userdata` | ~45-100+ GB | User storage & apps |
| `metadata` | varies | Encryption metadata |

### GPT Metadata
| Partition | Size | Location |
|-----------|------|----------|
| `pgpt` (Primary GPT) | ~17 KB (34 sectors) | Start of UFS LU0 (LBA 0-33) |
| `sgpt` (Secondary GPT) | ~17 KB (33 sectors) | End of UFS LU0 |

---

## 3. mtkclient Commands Reference

### Detection & Info
```bash
python mtk.py printgpt                    # Print partition table
python mtk.py printgpt --soc=MT6785       # Force chipset if auto-detect fails
```

### Read / Backup
```bash
# Single partition
python mtk.py r boot boot_backup.img

# Multiple partitions (comma-separated)
python mtk.py r nvram,nvdata,nvcfg,proinfo,persist,protect1,protect2,seccfg \
  nvram.bin,nvdata.bin,nvcfg.bin,proinfo.bin,persist.bin,protect1.bin,protect2.bin,seccfg.bin

# Full device dump
python mtk.py r --all ./full_backup/
```

### Write / Flash
```bash
# Single partition
python mtk.py w boot boot.img

# Flash all images from a directory (filenames must match partition names)
python mtk.py wl ./images/

# Flash preloader (DANGEROUS — only if completely dead)
python mtk.py w preloader preloader_begonia.bin
```

### Erase
```bash
python mtk.py e userdata     # Factory reset
python mtk.py e metadata     # Clear encryption metadata
python mtk.py e frp          # Remove Factory Reset Protection
python mtk.py e cache        # Clear cache
```

### Security
```bash
python mtk.py da seccfg unlock   # Unlock bootloader via BROM bypass
python mtk.py da seccfg lock     # Relock bootloader
```

### Special Flags
```bash
--soc=MT6785                           # Force chipset
--preloader=preloader_begonia.bin      # Specify preloader for Preloader mode
--scatter MT6785_Android_scatter.txt   # Use scatter when GPT is destroyed
--debugmode                            # Enable USB packet debug logging
```

### Reset
```bash
python mtk.py reset            # Reboot device
```

---

## 4. Recommended Unbricking Sequence

### Phase 1: Backup Critical Data (ALWAYS DO THIS FIRST)
```bash
python mtk.py r nvram,nvdata,nvcfg,proinfo,persist,seccfg,protect1,protect2 \
  nvram.bin,nvdata.bin,nvcfg.bin,proinfo.bin,persist.bin,seccfg.bin,protect1.bin,protect2.bin
```

### Phase 2: Unlock Bootloader
```bash
python mtk.py da seccfg unlock
```

### Phase 3: Flash Low-Level Boot Firmware
```bash
python mtk.py w lk lk.img
python mtk.py w lk2 lk.img
python mtk.py w dtbo dtbo.img
python mtk.py w tee1 tee.img
python mtk.py w tee2 tee.img
python mtk.py w scp1 scp.img
python mtk.py w scp2 scp.img
python mtk.py w sspm_1 sspm.img
python mtk.py w sspm_2 sspm.img
python mtk.py w md1img md1img.img
python mtk.py w logo logo.img
```

### Phase 4: Flash Kernel & Recovery
```bash
python mtk.py w boot boot.img
python mtk.py w recovery recovery.img
python mtk.py w vbmeta vbmeta.img
```

### Phase 5: Flash OS
**Android 10/11 (MIUI 12/12.5 — with `super` partition):**
```bash
python mtk.py w super super.img
python mtk.py w cust cust.img
python mtk.py e userdata
python mtk.py e metadata
```

**Android 9 (MIUI 11 — legacy layout):**
```bash
python mtk.py w system system.img
python mtk.py w vendor vendor.img
python mtk.py w cust cust.img
python mtk.py e userdata
python mtk.py e cache
```

### Phase 6: Preloader (ONLY if completely dead)
```bash
# ⚠️ DO NOT flash unless phone is completely unresponsive
# ⚠️ Match your EXACT variant (begonia vs begoniain)
python mtk.py w preloader preloader_begonia.bin
```

### Phase 7: Reboot
```bash
python mtk.py reset
```

---

## 5. Fixing a Destroyed Partition Table (GPT)

### Diagnosis
```bash
python mtk.py printgpt
# If this errors with "Error reading gpt" → GPT is corrupted/destroyed
```

### Method A: Restore from Backup
If you previously backed up your GPT:
```bash
python mtk.py w gpt gpt_main.bin
```

### Method B: Rebuild Using Scatter File
If you have NO GPT backup, use the scatter file from the stock ROM:
```bash
python mtk.py wl ./images/ --scatter MT6785_Android_scatter.txt --preloader preloader_begonia.bin
```
> ⚠️ After GPT rebuild, you MUST flash ALL partition images (Phases 3-5 above).

### Method C: SP Flash Tool (PC only, not available in Termux)
SP Flash Tool's "Format All + Download" mode reconstructs the GPT automatically from the scatter file.

---

## 6. Entering BROM Mode

### Method 1: Volume Up + USB (Standard)
1. Power off the bricked phone completely
2. Hold **Volume UP**
3. While holding, connect USB cable (via OTG to host phone)
4. Hold for 5-10 seconds
5. Accept Android USB permission popup

### Method 2: Test Point (When Vol+USB fails)
Required when preloader is corrupted (phone doesn't respond at all):

1. **Remove back cover** (heat adhesive, use suction cup + pry tool)
2. **Remove motherboard bracket** (unscrew upper plastic cover)
3. **DISCONNECT BATTERY** (unplug battery ribbon cable)
4. **Short the test point** to ground using tweezers:
   - Test point is on the **top motherboard** near the **battery FPC connector**
   - Short the gold test pad to any nearby metal shield (ground)
5. **While shorting**, plug in USB cable
6. mtkclient will detect BROM mode
7. **Release tweezers** once mtkclient shows successful connection
8. Reconnect battery before booting

---

## 7. Common Issues & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `STATUS_SEC_AUTH_FILE_NEEDED` | SP Flash Tool needs auth | Use `mtkclient` instead (auto-bypasses SLA/DAA) |
| Device disconnects during flash | USB driver issues | Use Linux or install UsbDk on Windows |
| Invalid IMEI after unbrick | `nvram`/`nvdata` was erased | Restore from backup or use IMEI write tool |
| Black screen after flash | Wrong preloader variant | Flash correct variant (`begonia` vs `begoniain`) |
| `Error reading gpt` | Partition table destroyed | Use `--scatter` flag with mtkclient |
| `super` partition errors | Android 9 ↔ 10 mismatch | Match ROM version to partition layout |
| No BROM detection | Dead preloader | Use physical test point method |

---

## 8. Hardware Variant Differences

| Feature | `begonia` (Global/EU/RU/CN) | `begoniain` (India) |
|---------|---------------------------|---------------------|
| NFC | ✅ Yes | ❌ No |
| Partition Layout | Identical | Identical |
| `vendor` / `nvram` images | Region-specific | Region-specific |
| **Interchangeable?** | ⚠️ Do NOT cross-flash preloaders between variants |

---

## 9. XDA Community Resources

- **Primary Unbrick Thread:** https://xdaforums.com/t/guide-begonia-begoniain-how-to-unbrick-when-stuck-on-preloader-mode.4182967/
- **SP Flash Tool BROM Guide:** https://xdaforums.com/t/guide-redmi-note-8-pro-flashing-with-sp-flash-tool-in-brom-mode.4363363/
- **mtkclient (Open Source):** https://github.com/bkerler/mtkclient
