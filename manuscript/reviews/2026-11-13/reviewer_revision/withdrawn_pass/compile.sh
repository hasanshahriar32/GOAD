#!/usr/bin/env bash
# ==============================================================================
# compile.sh - Compile the IEEE Journal CertGraph Manuscript
# ==============================================================================

set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

echo "[*] Compiling CertGraph IEEE Journal Manuscript..."

tectonic_bin="$(command -v tectonic || true)"
if [[ -z "$tectonic_bin" && -x "$HOME/.local/bin/tectonic" ]]; then
    tectonic_bin="$HOME/.local/bin/tectonic"
fi

if [[ -n "$tectonic_bin" ]]; then
    echo "[+] Using tectonic..."
    "$tectonic_bin" main.tex
elif command -v pdflatex &> /dev/null; then
    echo "[+] Using pdflatex + bibtex..."
    pdflatex -halt-on-error -interaction=nonstopmode main.tex
    bibtex main
    pdflatex -halt-on-error -interaction=nonstopmode main.tex
    pdflatex -halt-on-error -interaction=nonstopmode main.tex
else
    echo "[-] No local LaTeX compiler found (pdflatex or tectonic)."
    echo "[*] You can install tectonic on Arch Linux via: sudo pacman -S tectonic"
    echo "[*] Or upload submission_files/CertGraph_IEEE_Professor_Revision.zip to Overleaf."
    exit 1
fi

echo "[+] Compilation successful: main.pdf generated!"
