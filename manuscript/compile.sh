#!/usr/bin/env bash
# ==============================================================================
# compile.sh - Compile the Standalone 1-Column CertGraph Manuscript
# ==============================================================================

set -euo pipefail

echo "[*] Compiling CertGraph 1-Column Manuscript..."

if command -v tectonic &> /dev/null; then
    echo "[+] Using tectonic..."
    tectonic main.tex
elif command -v pdflatex &> /dev/null; then
    echo "[+] Using pdflatex + bibtex..."
    pdflatex -interaction=nonstopmode main.tex
    bibtex main
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
else
    echo "[-] No local LaTeX compiler found (pdflatex or tectonic)."
    echo "[*] You can install tectonic on Arch Linux via: sudo pacman -S tectonic"
    echo "[*] Or upload CertGraph_SingleColumn_Manuscript.zip directly to Overleaf."
    exit 1
fi

echo "[+] Compilation successful: main.pdf generated!"
