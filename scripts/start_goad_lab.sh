#!/usr/bin/env bash
# ==============================================================================
# start_goad_lab.sh — On-Demand Ephemeral Launcher for GOAD VMs
# Powers on DC03 (Domain Controller) and SRV03 (Certificate Authority)
# Directly from the connected disk (/dev/sdc4) using KVM hardware acceleration.
#
# Connects both VMs over a shared virtual network so SRV03 reaches DC03.
# ZERO systemd background services. ZERO persistent auto-start overhead.
# ==============================================================================

set -euo pipefail

IMAGE_DIR="/run/media/m4x1d/255fb331-4ad9-49d7-92b8-080d9effb0ef/goad_vms"
DC03_IMG="${IMAGE_DIR}/provider_GOAD-DC03.img"
SRV03_IMG="${IMAGE_DIR}/provider_GOAD-SRV03.img"

if [ ! -f "$DC03_IMG" ] || [ ! -f "$SRV03_IMG" ]; then
    echo "[-] Error: Connected disk GOAD images not found at $IMAGE_DIR"
    exit 1
fi

# Ensure /run/media/hs32 symlink exists so QCOW2 backing box image resolves
if [ ! -L "/run/media/hs32" ]; then
    docker run --rm -v /run/media:/host_media alpine ln -sf m4x1d /host_media/hs32
fi

# Create shared internal bridge network for GOAD containers
docker network create goad-net 2>/dev/null || true

# 1. Launch GOAD-DC03
if docker ps --format '{{.Names}}' | grep -q 'goad-dc03'; then
    echo "[!] GOAD-DC03 is already running."
else
    echo "[*] Launching GOAD-DC03 (meereen.essos.local: 192.168.56.12)..."
    docker run --rm -d \
        --name goad-dc03 \
        --net goad-net \
        --device /dev/kvm \
        -v /run/media:/run/media:rslave \
        -p 55985:5985 \
        -p 55986:5986 \
        -p 10389:389 \
        -p 10088:88 \
        -p 10445:445 \
        alpine sh -c "
            apk add --no-cache qemu-system-x86_64 >/dev/null 2>&1
            qemu-system-x86_64 \
                -enable-kvm \
                -m 3072 \
                -smp 2 \
                -cpu host \
                -drive file=/run/media/hs32/255fb331-4ad9-49d7-92b8-080d9effb0ef/goad_vms/provider_GOAD-DC03.img,format=qcow2,if=virtio \
                -netdev user,id=mgmt,hostfwd=tcp::5985-:5985,hostfwd=tcp::5986-:5986,hostfwd=tcp::389-:389,hostfwd=tcp::88-:88,hostfwd=tcp::445-:445 \
                -device virtio-net-pci,netdev=mgmt \
                -netdev socket,id=lan,mcast=230.0.0.1:12345 \
                -device virtio-net-pci,netdev=lan,mac=52:54:00:56:12:03 \
                -display none
        "
    echo "[+] GOAD-DC03 container started."
fi

# 2. Launch GOAD-SRV03
if docker ps --format '{{.Names}}' | grep -q 'goad-srv03'; then
    echo "[!] GOAD-SRV03 is already running."
else
    echo "[*] Launching GOAD-SRV03 (braavos.essos.local: 192.168.56.23)..."
    docker run --rm -d \
        --name goad-srv03 \
        --net goad-net \
        --device /dev/kvm \
        -v /run/media:/run/media:rslave \
        -p 56985:5985 \
        -p 56986:5986 \
        -p 8080:80 \
        -p 8443:443 \
        alpine sh -c "
            apk add --no-cache qemu-system-x86_64 >/dev/null 2>&1
            qemu-system-x86_64 \
                -enable-kvm \
                -m 4096 \
                -smp 2 \
                -cpu host \
                -drive file=/run/media/hs32/255fb331-4ad9-49d7-92b8-080d9effb0ef/goad_vms/provider_GOAD-SRV03.img,format=qcow2,if=virtio \
                -netdev user,id=mgmt,hostfwd=tcp::5985-:5985,hostfwd=tcp::5986-:5986,hostfwd=tcp::80-:80,hostfwd=tcp::443-:443 \
                -device virtio-net-pci,netdev=mgmt \
                -netdev socket,id=lan,mcast=230.0.0.1:12345 \
                -device virtio-net-pci,netdev=lan,mac=52:54:00:56:23:03 \
                -display none
        "
    echo "[+] GOAD-SRV03 container started."
fi

echo "=========================================================="
echo " [+] GOAD Dual-VM Mesh Active on Connected Disk!         "
echo "  - DC03 (Domain Controller): 127.0.0.1:10389, 10445, 55985"
echo "  - SRV03 (Certificate Authority): 127.0.0.1:8080, 56985 "
echo "  - Internal Mesh Bus: 192.168.56.x (mcast 230.0.0.1)    "
echo "=========================================================="
