#!/usr/bin/env bash
# Compilation script for the CertGraph Thesis Paper
# Supports Typst (instant standalone), pdflatex + bibtex, latexmk, and tectonic

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "Compiling CertGraph Final Year Thesis Paper (HSTU Format)"
echo "Directory: $DIR"
echo "=========================================================="

TYPST_BIN="$(command -v typst 2>/dev/null || echo '/home/hs32/.local/bin/typst')"

if [ -x "$TYPST_BIN" ]; then
    echo "[+] Compiling via standalone document engine ($TYPST_BIN)..."
    "$TYPST_BIN" compile thesis.typ thesis.pdf
    echo "[✓] Compilation successful! Output: thesis.pdf"
elif command -v latexmk &> /dev/null; then
    echo "[+] Found latexmk. Compiling LaTeX via latexmk..."
    latexmk -pdf -interaction=nonstopmode -shell-escape main.tex
    echo "[✓] Compilation successful! Output: main.pdf"
elif command -v pdflatex &> /dev/null; then
    echo "[+] Found pdflatex. Compiling LaTeX via standard multi-pass..."
    pdflatex -interaction=nonstopmode main.tex
    bibtex main || true
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
    echo "[✓] Compilation successful! Output: main.pdf"
elif command -v tectonic &> /dev/null; then
    echo "[+] Found tectonic. Compiling LaTeX via tectonic..."
    tectonic main.tex
    echo "[✓] Compilation successful! Output: main.pdf"
else
    echo "[-] No local compiler found."
    echo "    To compile on Overleaf: Zip the entire thesis_paper directory and upload to overleaf.com"
fi
