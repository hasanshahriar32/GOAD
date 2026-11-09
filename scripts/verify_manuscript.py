#!/usr/bin/env python3
"""
verify_manuscript.py - Strict Validation of LaTeX Citations, Labels, and References
"""

import re
import glob
import sys
import os

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manuscript_dir = os.path.join(root, "manuscript")
    bib_file = os.path.join(manuscript_dir, "references.bib")

    cite_pat = re.compile(r"\\cite[a-z]*\{([^}]+)\}")
    ref_pat = re.compile(r"\\(?:ref|eqref|autoref)\{([^}]+)\}")
    label_pat = re.compile(r"\\label\{([^}]+)\}|(?:^|[,\s\[])label=\{?([a-zA-Z0-9_\-:]+)\}?")
    bib_key_pat = re.compile(r"@\w+\s*\{\s*([^,]+),")

    cites = set()
    labels = set()
    refs = set()
    cite_locations = {}

    for path in glob.glob(os.path.join(manuscript_dir, "**", "*.tex"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                for m in cite_pat.finditer(line):
                    for k in m.group(1).split(","):
                        k = k.strip()
                        if k:
                            cites.add(k)
                            cite_locations.setdefault(k, []).append((os.path.basename(path), line_no))
                for m in ref_pat.finditer(line):
                    refs.add(m.group(1).strip())
                for m in label_pat.finditer(line):
                    lbl = m.group(1) or m.group(2)
                    if lbl:
                        labels.add(lbl.strip())

    bib_keys = []
    with open(bib_file, "r", encoding="utf-8") as f:
        for line in f:
            m = bib_key_pat.match(line.strip())
            if m:
                bib_keys.append(m.group(1).strip())

    bib_key_set = set(bib_keys)
    missing_cites = cites - bib_key_set
    missing_refs = refs - labels
    dup_bib_keys = [k for k in bib_key_set if bib_keys.count(k) > 1]

    print("=" * 65)
    print("      CERTGRAPH MANUSCRIPT & BIBTEX VERIFICATION AUDIT")
    print("=" * 65)
    print(f"[*] Total unique citations in manuscript: {len(cites)}")
    print(f"[*] Total entries in references.bib:     {len(bib_key_set)}")
    print(f"[*] Total labels found:                 {len(labels)}")
    print(f"[*] Total references found:             {len(refs)}")

    errors = 0

    if missing_cites:
        print(f"\n[-] FAILED: {len(missing_cites)} missing citation keys in references.bib:")
        for k in sorted(missing_cites):
            print(f"    - {k} (used in: {cite_locations[k]})")
        errors += 1
    else:
        print("[+] SUCCESS: 0 missing citation keys!")

    if dup_bib_keys:
        print(f"\n[-] FAILED: {len(dup_bib_keys)} duplicate keys in references.bib:")
        for k in sorted(dup_bib_keys):
            print(f"    - {k}")
        errors += 1
    else:
        print("[+] SUCCESS: 0 duplicate keys in references.bib!")

    if missing_refs:
        print(f"\n[-] FAILED: {len(missing_refs)} undefined references:")
        for r in sorted(missing_refs):
            print(f"    - {r}")
        errors += 1
    else:
        print("[+] SUCCESS: 0 undefined reference labels!")

    print("=" * 65)
    if errors > 0:
        print("[-] AUDIT FAILED WITH ERRORS.")
        sys.exit(1)
    else:
        print("[+] ALL AUDIT CHECKS PASSED SUCCESSFULLY (100% CLEAN)!")
        sys.exit(0)

if __name__ == "__main__":
    main()
