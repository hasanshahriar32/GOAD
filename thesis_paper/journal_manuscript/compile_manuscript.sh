#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "   COMPILING IEEE TRANSACTIONS JOURNAL MANUSCRIPT (TECTONIC)     "
echo "=================================================================="

# Use local tectonic binary
TECTONIC="/home/hs32/.local/bin/tectonic"
if [ ! -f "$TECTONIC" ]; then
    TECTONIC="tectonic"
fi

echo "[1/2] Compiling manuscript.tex with Tectonic..."
"$TECTONIC" -X compile manuscript.tex

echo "[2/2] Verifying output..."
if [ -f "manuscript.pdf" ]; then
    PAGES=$(pdfinfo manuscript.pdf 2>/dev/null | grep Pages | awk '{print $2}' || echo "N/A")
    SIZE=$(du -h manuscript.pdf | cut -f1)
    echo "[✓] Successfully compiled: manuscript.pdf ($SIZE, $PAGES pages)"
    if [[ "${1:-}" == "--copy-to-desktop" ]]; then
        cp manuscript.pdf "$HOME/Desktop/manuscript.pdf"
        echo "[✓] Copied to Desktop"
    fi
else
    echo "[!] Error: manuscript.pdf was not generated."
    exit 1
fi
