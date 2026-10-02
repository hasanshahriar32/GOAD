@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: Compilation script for the CertGraph Thesis Paper (Windows CMD / Batch)
:: Compiles the full-fledged, multi-chapter final-year thesis monograph (HSTU ECE Format)
:: Supports: Tectonic (primary offline engine), latexmk, pdflatex, and Typst
:: ==============================================================================

cd /d "%~dp0"

echo ==========================================================
echo Compiling CertGraph Final Year Thesis Paper (HSTU Format)
echo Directory: %CD%
echo ==========================================================

:: 1. Search for Tectonic in PATH or common Windows install locations
set "TECTONIC_BIN="
where tectonic >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "TECTONIC_BIN=tectonic"
) else if exist "%USERPROFILE%\.cargo\bin\tectonic.exe" (
    set "TECTONIC_BIN=%USERPROFILE%\.cargo\bin\tectonic.exe"
) else if exist "%LOCALAPPDATA%\Programs\Tectonic\tectonic.exe" (
    set "TECTONIC_BIN=%LOCALAPPDATA%\Programs\Tectonic\tectonic.exe"
) else if exist "%USERPROFILE%\scoop\shims\tectonic.exe" (
    set "TECTONIC_BIN=%USERPROFILE%\scoop\shims\tectonic.exe"
) else if exist "C:\ProgramData\chocolatey\bin\tectonic.exe" (
    set "TECTONIC_BIN=C:\ProgramData\chocolatey\bin\tectonic.exe"
)

:: 2. Search for Typst in PATH or common Windows install locations
set "TYPST_BIN="
where typst >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "TYPST_BIN=typst"
) else if exist "%USERPROFILE%\.cargo\bin\typst.exe" (
    set "TYPST_BIN=%USERPROFILE%\.cargo\bin\typst.exe"
) else if exist "%LOCALAPPDATA%\Programs\typst\typst.exe" (
    set "TYPST_BIN=%LOCALAPPDATA%\Programs\typst\typst.exe"
) else if exist "%USERPROFILE%\scoop\shims\typst.exe" (
    set "TYPST_BIN=%USERPROFILE%\scoop\shims\typst.exe"
) else if exist "C:\ProgramData\chocolatey\bin\typst.exe" (
    set "TYPST_BIN=C:\ProgramData\chocolatey\bin\typst.exe"
)

:: 3. Execute Compiler Pipeline
if defined TECTONIC_BIN (
    echo [+] Found Tectonic: !TECTONIC_BIN!
    echo [+] Compiling full 100+ page monograph from main.tex...
    "!TECTONIC_BIN!" main.tex
    if !ERRORLEVEL! neq 0 (
        echo [-] Tectonic compilation failed.
        goto :error
    )
    copy /y main.pdf thesis.pdf >nul
    echo [✓] Compilation successful!
    echo     Output files:
    echo     - main.pdf
    echo     - thesis.pdf
    goto :success
)

:: Check for latexmk in PATH or MiKTeX / TeX Live
where latexmk >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [+] Found latexmk. Compiling LaTeX via latexmk...
    latexmk -pdf -interaction=nonstopmode -shell-escape main.tex
    if !ERRORLEVEL! neq 0 (
        echo [-] latexmk compilation failed.
        goto :error
    )
    copy /y main.pdf thesis.pdf >nul
    echo [✓] Compilation successful! Output: main.pdf and thesis.pdf
    goto :success
)

:: Check for pdflatex in PATH or MiKTeX / TeX Live
where pdflatex >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [+] Found pdflatex. Compiling LaTeX via standard multi-pass...
    pdflatex -interaction=nonstopmode main.tex
    where bibtex >nul 2>&1 && bibtex main
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
    if not exist main.pdf (
        echo [-] pdflatex compilation failed.
        goto :error
    )
    copy /y main.pdf thesis.pdf >nul
    echo [✓] Compilation successful! Output: main.pdf and thesis.pdf
    goto :success
)

:: Check for Typst
if defined TYPST_BIN (
    echo [+] Found Typst: !TYPST_BIN!
    echo [+] Compiling standalone thesis document via Typst...
    "!TYPST_BIN!" compile thesis.typ thesis.pdf
    if !ERRORLEVEL! neq 0 (
        echo [-] Typst compilation failed.
        goto :error
    )
    copy /y thesis.pdf typst_thesis.pdf >nul
    echo [✓] Compilation successful! Output: thesis.pdf
    goto :success
)

echo [-] No local compiler found (Tectonic, latexmk, pdflatex, or Typst).
echo     To compile on Windows, you can install one of the following:
echo     1. Tectonic: winget install --id AnkeK.Tectonic  or  cargo install tectonic
echo     2. MiKTeX:   https://miktex.org/download
echo     3. Typst:    winget install --id Typst.Typst    or  cargo install typst-cli
echo     Alternatively, upload the zipped thesis_paper folder to Overleaf (overleaf.com).
goto :error

:success
echo ==========================================================
echo [✓] Build completed successfully.
echo ==========================================================
if "%~1"=="--no-pause" exit /b 0
timeout /t 5 >nul 2>&1 || pause
exit /b 0

:error
echo ==========================================================
echo [-] Build encountered errors.
echo ==========================================================
if "%~1"=="--no-pause" exit /b 1
pause
exit /b 1
