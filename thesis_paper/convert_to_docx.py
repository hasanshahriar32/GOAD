#!/usr/bin/env python3
"""
Convert the compiled CertGraph Thesis Monograph PDF to DOCX format (Microsoft Word).
Utilizes multi-processing across available CPU cores for fast, high-fidelity conversion.
"""

import sys
import os
import time
from pdf2docx import Converter

def main():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dir_path)

    pdf_file = "main.pdf"
    if not os.path.exists(pdf_file):
        if os.path.exists("thesis.pdf"):
            pdf_file = "thesis.pdf"
        else:
            print(f"[-] Error: Could not find {pdf_file} or thesis.pdf.")
            sys.exit(1)

    docx_file = "thesis.docx"
    print(f"[+] Converting '{pdf_file}' to '{docx_file}' using multi-processing...")
    start_time = time.time()

    cv = Converter(pdf_file)
    cv.convert(docx_file, multi_processing=True, cpu_count=8)
    cv.close()

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(docx_file) / (1024 * 1024)
    print(f"[✓] Conversion complete! Created '{docx_file}' ({file_size_mb:.2f} MB) in {elapsed:.1f}s.")

if __name__ == "__main__":
    main()
