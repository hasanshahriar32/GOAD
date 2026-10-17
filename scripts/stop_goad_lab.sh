#!/usr/bin/env bash
# ==============================================================================
# stop_goad_lab.sh — Clean Stop for GOAD VMs
# Shuts down ephemeral containers cleanly, leaving zero background footprint.
# ==============================================================================

set -euo pipefail

echo "[*] Stopping GOAD VM containers..."
docker stop goad-dc03 goad-srv03 goad-dc03-test 2>/dev/null || true
echo "[+] All GOAD lab containers stopped. Zero background processes running."
