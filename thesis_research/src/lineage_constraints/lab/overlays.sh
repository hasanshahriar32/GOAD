#!/usr/bin/env bash
# Isolated research VMs. All writes go to new overlays, never to source images.
set -euo pipefail

action="${1:-status}"
evidence_root="${GOAD_EVIDENCE_ROOT:-/run/media/m4x1d/255fb331-4ad9-49d7-92b8-080d9effb0ef}"
lab_state="${GOAD_LINEAGE_STATE:-/tmp/goad-lineage-lab}"
legacy_mount="/run/media/hs32/255fb331-4ad9-49d7-92b8-080d9effb0ef"
tool_image="goad-lineage-qemu:local"
network="goad-lineage-isolated"
disk_bus="${GOAD_LINEAGE_DISK_BUS:-ide}"

case "$action" in
  start)
    mkdir -p "$lab_state"
    docker network inspect "$network" >/dev/null 2>&1 || docker network create "$network"
    for node in DC03 SRV03; do
      lower_node="${node,,}"
      container="goad-lineage-$lower_node"
      overlay="$lower_node.qcow2"
      if [[ ! -f "$lab_state/$overlay" ]]; then
        docker run --rm --network none --entrypoint qemu-img \
          -v "$evidence_root:$legacy_mount:ro" -v "$lab_state:/lab" "$tool_image" \
          create -f qcow2 -F qcow2 -b "$legacy_mount/goad_vms/provider_GOAD-$node.img" "/lab/$overlay"
      fi
      if docker container inspect "$container" >/dev/null 2>&1; then
        echo "$container already exists; inspect it before another start" >&2
        exit 1
      fi
      if [[ "$node" == DC03 ]]; then
        winrm_port=55985
        kerberos_port=10088
        mac="52:54:00:56:12:03"
        lan="socket,id=lan,listen=:12000"
        recovery_mac="52:54:00:56:12:99"
      else
        winrm_port=56985
        kerberos_port=11088
        mac="52:54:00:56:23:03"
        lan="socket,id=lan,connect=goad-lineage-dc03:12000"
        recovery_mac="52:54:00:56:23:99"
      fi
      recovery_args=()
      if [[ "${GOAD_LINEAGE_RECOVERY:-1}" == 1 ]]; then
        # Reuse the recovery NIC identity inventoried in the writable overlays.
        # This management network is local to each QEMU process, with outbound
        # guest traffic restricted. No source image is changed.
        recovery_args=(-netdev "user,id=recovery,net=10.20.0.0/24,dhcpstart=10.20.0.15,restrict=on,hostfwd=tcp::15985-10.20.0.15:5985,hostfwd=tcp::18888-10.20.0.15:88,hostfwd=tcp::1389-10.20.0.15:389,hostfwd=tcp::1636-10.20.0.15:636,hostfwd=tcp::15353-10.20.0.15:53,hostfwd=udp::15353-10.20.0.15:53"
                       -device "e1000,netdev=recovery,id=recovery0,mac=$recovery_mac")
      fi
      docker run -d --name "$container" --network "$network" --device /dev/kvm \
        --memory 3500m --cpus 2 \
        -v "$evidence_root:$legacy_mount:ro" -v "$lab_state:/lab" \
        -p "127.0.0.1:$winrm_port:5985" -p "127.0.0.1:$kerberos_port:88" \
        "$tool_image" -enable-kvm -m 2560 -smp 2 -cpu host \
        -drive "file=/lab/$overlay,format=qcow2,if=$disk_bus" \
        -netdev user,id=mgmt,restrict=on,hostfwd=tcp::5985-:5985,hostfwd=tcp::88-:88 \
        -device virtio-net-pci,netdev=mgmt \
        -netdev "$lan" \
        -device "virtio-net-pci,netdev=lan,mac=$mac" \
        "${recovery_args[@]}" \
        -monitor tcp:127.0.0.1:4444,server=on,wait=off -display none
    done
    ;;
  stop)
    for node in dc03 srv03; do
      if docker container inspect "goad-lineage-$node" >/dev/null 2>&1; then
        docker stop -t 20 "goad-lineage-$node"
        docker rm "goad-lineage-$node"
      fi
    done
    ;;
  status)
    docker ps -a --filter name=goad-lineage- --format '{{.Names}} {{.Status}}'
    ;;
  *) echo "Usage: $0 start|stop|status" >&2; exit 2 ;;
esac
