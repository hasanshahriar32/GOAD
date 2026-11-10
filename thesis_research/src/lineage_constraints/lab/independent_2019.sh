#!/usr/bin/env bash
# Fresh independent Windows 2019 instance; the stock source image stays read-only.
set -euo pipefail
action="${1:-status}"
name=goad-lineage-win2019
source_root="${GOAD_EVIDENCE_ROOT:-/run/media/m4x1d/255fb331-4ad9-49d7-92b8-080d9effb0ef}"
state="${GOAD_Q1_2019_STATE:-/tmp/goad-q1-independent-2019}"
image=goad-lineage-qemu:local
base=/source/goad_vms/jborean93-VAGRANTSLASH-WindowsServer2019_vagrant_box_image_1.2.0_box.img
case "$action" in
  start)
    if docker container inspect "$name" >/dev/null 2>&1; then
      echo "$name already exists" >&2; exit 1
    fi
    mkdir -p "$state"
    media_args=()
    if [[ -f "$state/updates.iso" ]]; then
      media_args=(-drive "file=/lab/updates.iso,media=cdrom,readonly=on,if=ide")
    fi
    if [[ ! -f "$state/windows2019.qcow2" ]]; then
      docker run --rm --network none --entrypoint qemu-img \
        -v "$source_root:/source:ro" -v "$state:/lab" "$image" \
        create -f qcow2 -F qcow2 -b "$base" /lab/windows2019.qcow2
    fi
    docker run -d --name "$name" --network goad-lineage-isolated --device /dev/kvm \
      --memory "${GOAD_Q1_2019_MEMORY_LIMIT:-2800m}" --cpus 2 -v "$source_root:/source:ro" -v "$state:/lab" \
      -p 127.0.0.1:57985:15985 -p 127.0.0.3:88:18888 \
      -p 127.0.0.3:389:1389 -p 127.0.0.3:636:1636 \
      "$image" -enable-kvm -m "${GOAD_Q1_2019_RAM_MB:-2048}" -smp 2 -cpu host \
      -drive file=/lab/windows2019.qcow2,format=qcow2,if=ide \
      "${media_args[@]}" \
      -netdev user,id=mgmt,net=10.21.0.0/24,dhcpstart=10.21.0.15,restrict=on,hostfwd=tcp::15985-10.21.0.15:5985,hostfwd=tcp::18888-10.21.0.15:88,hostfwd=tcp::1389-10.21.0.15:389,hostfwd=tcp::1636-10.21.0.15:636 \
      -device e1000,netdev=mgmt,mac=52:54:00:21:19:01 \
      -monitor tcp:127.0.0.1:4444,server=on,wait=off -display none
    ;;
  stop)
    if docker container inspect "$name" >/dev/null 2>&1; then docker stop -t 20 "$name"; docker rm "$name"; fi
    ;;
  status) docker ps -a --filter name="$name" --format '{{.Names}} {{.Status}}' ;;
  *) echo "Usage: $0 start|stop|status" >&2; exit 2 ;;
esac
