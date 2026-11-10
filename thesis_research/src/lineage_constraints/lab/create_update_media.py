"""Create read-only update media from Microsoft Catalog downloads.

The SHA-1 in the official download filename and a locally recorded SHA-256 are
checked. Windows servicing must also validate the package; hashes alone do not
establish publisher trust. No private credentials are included in the media.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

import pycdlib


def create(downloads,output,manifest):
    if output.exists() or manifest.exists():raise FileExistsError("Refusing media/manifest overwrite")
    catalog=json.loads((downloads/"catalog.json").read_text());records=[]
    for item in catalog:
        path=downloads/item["urls"][0].rsplit("/",1)[-1]
        sha1=hashlib.sha1();sha256=hashlib.sha256();size=0
        with path.open("rb") as source:
            for data in iter(lambda:source.read(1024*1024),b""):
                sha1.update(data);sha256.update(data);size+=len(data)
        expected=re.search(r"_([0-9a-f]{40})\.msu$",path.name).group(1)
        if sha1.hexdigest()!=expected:raise ValueError("Official filename content digest differs: "+path.name)
        records.append({**item,"bytes":size,"sha1":sha1.hexdigest(),"sha256":sha256.hexdigest(),"file":path.name})
    manifest.write_text(json.dumps({"packages":records,"scope":"Independent writable Windows 2019 research copy only; July 2025 prerequisite then October 2026 security cumulative update",
        "installation_contract":"Normal Windows servicing signature/applicability checks; never IgnoreCheck",
        "support_sources":["https://support.microsoft.com/en-us/servicing/os/windows-10/2025/07/july-8-2025-kb5062557-os-build-17763-7558",
                           "https://support.microsoft.com/en-us/servicing/os/windows-10/2026/10/kb5126651-windows-10-1809-security-update"]},indent=2)+"\n")
    iso=pycdlib.PyCdlib();iso.new(interchange_level=3,joliet=3,vol_ident="Q1_UPDATES")
    for record,name in zip(records,("JULY25.MSU","OCT26.MSU"),strict=True):
        iso.add_file(str(downloads/record["file"]),iso_path="/"+name+";1",joliet_path="/"+name)
    iso.add_file(str(manifest),iso_path="/MANIFEST.JSON;1",joliet_path="/manifest.json")
    iso.write(str(output));iso.close()
    print(json.dumps({"media":str(output),"packages":[{k:r[k] for k in ("kb","bytes","sha256")} for r in records]},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("downloads",type=Path);parser.add_argument("output",type=Path);parser.add_argument("manifest",type=Path)
    args=parser.parse_args();create(args.downloads,args.output,args.manifest)
