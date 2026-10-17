#!/usr/bin/env bash
# ==============================================================================
# test_vm_boot.sh — Ephemeral QEMU/KVM Launcher for GOAD VMs on Connected Disk
# ==============================================================================

set -euo pipefail

IMAGE_DIR="/run/media/m4x1d/255fb331-4ad9-49d7-92b8-080d9effb0ef/goad_vms"
DC03_IMG="${IMAGE_DIR}/provider_GOAD-DC03.img"
SRV03_IMG="${IMAGE_DIR}/provider_GOAD-SRV03.img"

echo "[*] Checking VM disk images..."
if [ ! -f "$DC03_IMG" ]; then
    echo "[-] Error: DC03 image not found at $DC03_IMG"
    exit 1
fi

echo "[+] DC03 Image verified: $DC03_IMG ($(du -h "$DC03_IMG" | cut -f1))"
echo "[+] Starting DC03 in background using QEMU-KVM with ephemeral snapshot protection..."

docker run --rm -d \
    --name goad-dc03-test \
    --device /dev/kvm \
    -v /run/media:/run/media \
    -p 55985:5985 \
    -p 55986:5986 \
    -p 10389:389 \
    -p 10088:88 \
    -p 10445:445 \
    alpine sh -c "
        apk add --no-cache qemu-system-x86_64 >/dev/null 2>&1
        echo '[+] Launching QEMU for GOAD-DC03...'
        qemu-system-x86_64 \
            -enable-kvm \
            -m 3072 \
            -smp 2 \
            -cpu host \
            -drive file=/run/media/hs32/255fb331-4ad9-49d7-92b8-080d9effb0ef/goad_vms/provider_GOAD-DC03.img,format=qcow2,if=virtio \
            -net nic,model=virtio \
            -net user,hostfwd=tcp::5985-:5985,hostfwd=tcp::5986-:5986,hostfwd=tcp::389-:389,hostfwd=tcp::88-:88,hostfwd=tcp::445-:445 \
            -display none \
            -snapshot
    "

echo "[+] Container goad-dc03-test launched."
echo "[*] Waiting for VM boot (checking WinRM port 55985 / LDAP port 10389)..."
