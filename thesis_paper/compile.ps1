# ==============================================================================
# Compilation script for the CertGraph Thesis Paper (Windows PowerShell)
# Compiles the full-fledged, multi-chapter final-year thesis monograph (HSTU ECE Format)
# Supports: Tectonic (primary offline engine), latexmk, pdflatex, and Typst
#
# Usage:
#   .\compile.ps1            (Interactive)
#   .\compile.ps1 -OpenPdf   (Compiles and automatically opens thesis.pdf)
#   .\compile.ps1 -NoPause   (Non-interactive for automated pipelines)
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$NoPause,
    [switch]$OpenPdf
)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($ScriptDir) { Set-Location $ScriptDir }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Compiling CertGraph Final Year Thesis Paper (HSTU Format)" -ForegroundColor Cyan
Write-Host "Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Search for Tectonic
$TectonicCmd = Get-Command tectonic -ErrorAction SilentlyContinue
$Tectonic = if ($TectonicCmd) { $TectonicCmd.Source } else { $null }
if (-not $Tectonic) {
    $TectonicCandidates = @(
        "$env:USERPROFILE\.cargo\bin\tectonic.exe",
        "$env:LOCALAPPDATA\Programs\Tectonic\tectonic.exe",
        "$env:USERPROFILE\scoop\shims\tectonic.exe",
        "C:\ProgramData\chocolatey\bin\tectonic.exe"
    )
    foreach ($cand in $TectonicCandidates) {
        if (Test-Path $cand) { $Tectonic = $cand; break }
    }
}

# 2. Search for Typst
$TypstCmd = Get-Command typst -ErrorAction SilentlyContinue
$Typst = if ($TypstCmd) { $TypstCmd.Source } else { $null }
if (-not $Typst) {
    $TypstCandidates = @(
        "$env:USERPROFILE\.cargo\bin\typst.exe",
        "$env:LOCALAPPDATA\Programs\typst\typst.exe",
        "$env:USERPROFILE\scoop\shims\typst.exe",
        "C:\ProgramData\chocolatey\bin\typst.exe"
    )
    foreach ($cand in $TypstCandidates) {
        if (Test-Path $cand) { $Typst = $cand; break }
    }
}

$LatexmkCmd = Get-Command latexmk -ErrorAction SilentlyContinue
$Latexmk = if ($LatexmkCmd) { $LatexmkCmd.Source } else { $null }
$PdfLatexCmd = Get-Command pdflatex -ErrorAction SilentlyContinue
$PdfLatex = if ($PdfLatexCmd) { $PdfLatexCmd.Source } else { $null }

$BuildSuccess = $false

if ($Tectonic) {
    Write-Host "[+] Found Tectonic: $Tectonic" -ForegroundColor Green
    Write-Host "[+] Compiling full 100+ page monograph from main.tex..." -ForegroundColor Green
    & $Tectonic main.tex
    if ($LASTEXITCODE -eq 0 -and (Test-Path "main.pdf")) {
        Copy-Item -Force "main.pdf" "thesis.pdf"
        $BuildSuccess = $true
    }
}
elseif ($Latexmk) {
    Write-Host "[+] Found latexmk: $Latexmk. Compiling LaTeX..." -ForegroundColor Green
    & latexmk -pdf -interaction=nonstopmode -shell-escape main.tex
    if ($LASTEXITCODE -eq 0 -and (Test-Path "main.pdf")) {
        Copy-Item -Force "main.pdf" "thesis.pdf"
        $BuildSuccess = $true
    }
}
elseif ($PdfLatex) {
    Write-Host "[+] Found pdflatex: $PdfLatex. Compiling via standard multi-pass..." -ForegroundColor Green
    & pdflatex -interaction=nonstopmode main.tex
    if (Get-Command bibtex -ErrorAction SilentlyContinue) {
        try { & bibtex main } catch {}
    }
    & pdflatex -interaction=nonstopmode main.tex
    & pdflatex -interaction=nonstopmode main.tex
    if (Test-Path "main.pdf") {
        Copy-Item -Force "main.pdf" "thesis.pdf"
        $BuildSuccess = $true
    }
}
elseif ($Typst) {
    Write-Host "[+] Found Typst: $Typst. Compiling standalone document..." -ForegroundColor Green
    & $Typst compile thesis.typ thesis.pdf
    if ($LASTEXITCODE -eq 0 -and (Test-Path "thesis.pdf")) {
        Copy-Item -Force "thesis.pdf" "typst_thesis.pdf"
        $BuildSuccess = $true
    }
}
else {
    Write-Host "[-] No local compiler found (Tectonic, latexmk, pdflatex, or Typst)." -ForegroundColor Red
    Write-Host "    To install on Windows:" -ForegroundColor Yellow
    Write-Host "    1. Tectonic: winget install --id AnkeK.Tectonic  or  cargo install tectonic" -ForegroundColor Yellow
    Write-Host "    2. MiKTeX:   https://miktex.org/download" -ForegroundColor Yellow
    Write-Host "    3. Typst:    winget install --id Typst.Typst    or  cargo install typst-cli" -ForegroundColor Yellow
    Write-Host "    Alternatively, upload the zipped folder to Overleaf (overleaf.com)." -ForegroundColor Yellow
}

if ($BuildSuccess) {
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "[✓] Compilation successful!" -ForegroundColor Green
    Write-Host "    Output files: main.pdf and thesis.pdf" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    if ($OpenPdf) {
        Start-Process "thesis.pdf"
    }
} else {
    Write-Host "`n==========================================================" -ForegroundColor Red
    Write-Host "[-] Build encountered errors." -ForegroundColor Red
    Write-Host "==========================================================" -ForegroundColor Red
}

if (-not $NoPause) {
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
