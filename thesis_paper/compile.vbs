' ==============================================================================
' Compilation script for the CertGraph Thesis Paper (Windows VBScript)
' Compiles the full-fledged, multi-chapter final-year thesis monograph (HSTU ECE Format)
' Supports: Tectonic (primary offline engine), latexmk, pdflatex, and Typst
'
' Usage:
'   1. Double-click "compile.vbs" in Windows Explorer to compile.
'   2. A console window will show compilation progress in real-time.
'   3. Upon completion, an interactive dialog prompts to view the resulting thesis.pdf.
' ==============================================================================
Option Explicit

Dim objShell, objFSO, scriptDir, batPath, pdfPath, intReturn, userChoice

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Resolve script directory and set working directory
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = scriptDir

batPath = scriptDir & "\compile.bat"
pdfPath = scriptDir & "\thesis.pdf"

' 1. If compile.bat exists, run it via cmd.exe in a visible window (1) and wait (True)
If objFSO.FileExists(batPath) Then
    intReturn = objShell.Run("cmd.exe /c ""compile.bat"" --no-pause", 1, True)
Else
    ' Fallback: Direct command execution if compile.bat is absent
    intReturn = objShell.Run("cmd.exe /c ""tectonic main.tex && copy /y main.pdf thesis.pdf""", 1, True)
End If

' 2. Inspect exit code and generated PDF artifact
If intReturn = 0 And objFSO.FileExists(pdfPath) Then
    userChoice = MsgBox("✓ CertGraph Final Year Thesis compiled successfully!" & vbCrLf & vbCrLf & _
                        "Output File: thesis.pdf (and main.pdf)" & vbCrLf & _
                        "Location: " & scriptDir & vbCrLf & vbCrLf & _
                        "Would you like to open thesis.pdf now?", _
                        vbYesNo + vbInformation + vbDefaultButton1, _
                        "CertGraph Thesis - Build Succeeded")
    
    If userChoice = vbYes Then
        objShell.Run """" & pdfPath & """"
    End If
Else
    MsgBox "[-] Thesis compilation encountered an error (Exit Code: " & intReturn & ")." & vbCrLf & vbCrLf & _
           "Please ensure a LaTeX or Typst engine is installed on Windows:" & vbCrLf & _
           "  1. Tectonic: winget install --id AnkeK.Tectonic" & vbCrLf & _
           "  2. MiKTeX:   https://miktex.org/download" & vbCrLf & _
           "  3. Typst:    winget install --id Typst.Typst" & vbCrLf & vbCrLf & _
           "Alternatively, upload the zipped folder to Overleaf (overleaf.com).", _
           vbCritical, _
           "CertGraph Thesis - Build Failed"
End If

Set objFSO = Nothing
Set objShell = Nothing
