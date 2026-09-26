#!/usr/bin/env bash
# Compilation script for the CertGraph Thesis Paper
# Compiles the full-fledged, multi-chapter final-year thesis monograph (HSTU ECE Format)
# Supports Tectonic (primary offline LaTeX engine), latexmk, pdflatex, and Typst

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "Compiling CertGraph Final Year Thesis Paper (HSTU Format)"
echo "Directory: $DIR"
echo "=========================================================="

TECTONIC_BIN="$(command -v tectonic 2>/dev/null || echo '/home/hs32/.local/bin/tectonic')"
TYPST_BIN="$(command -v typst 2>/dev/null || echo '/home/hs32/.local/bin/typst')"

if [ -x "$TECTONIC_BIN" ]; then
    echo "[+] Found Tectonic ($TECTONIC_BIN)."
    echo "[+] Compiling full 100+ page monograph from main.tex..."
    "$TECTONIC_BIN" main.tex
    cp -f main.pdf thesis.pdf
    echo "[✓] Compilation successful!"
    echo "    Output files:"
    echo "    - main.pdf ($(pdfinfo main.pdf 2>/dev/null | grep -i 'Pages:' | awk '{print $2}') pages)"
    echo "    - thesis.pdf ($(pdfinfo thesis.pdf 2>/dev/null | grep -i 'Pages:' | awk '{print $2}') pages)"
elif command -v latexmk &> /dev/null; then
    echo "[+] Found latexmk. Compiling LaTeX via latexmk..."
    latexmk -pdf -interaction=nonstopmode -shell-escape main.tex
    cp -f main.pdf thesis.pdf
    echo "[✓] Compilation successful! Output: main.pdf and thesis.pdf"
elif command -v pdflatex &> /dev/null; then
    echo "[+] Found pdflatex. Compiling LaTeX via standard multi-pass..."
    pdflatex -interaction=nonstopmode main.tex
    bibtex main || true
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
    cp -f main.pdf thesis.pdf
    echo "[✓] Compilation successful! Output: main.pdf and thesis.pdf"
elif [ -x "$TYPST_BIN" ]; then
    echo "[+] Found Typst ($TYPST_BIN). Compiling standalone document..."
    "$TYPST_BIN" compile thesis.typ thesis.pdf
    echo "[✓] Compilation successful! Output: thesis.pdf"
else
    echo "[-] No local compiler found."
    echo "    To compile on Overleaf: Zip the entire thesis_paper directory and upload to overleaf.com"
fi
