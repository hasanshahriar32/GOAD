"""Read-only integrity/style/privacy audit of the local research deliverable."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RESULTS=ROOT/"thesis_research/results/lineage_constraints/2026-11-10"
DATA=ROOT/"thesis_research/data/lineage_live/2026-11-10"


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def simple_manifest(directory):
    manifest=json.loads((directory/"manifest.json").read_text());checked=0
    for name,expected in manifest.items():
        if not isinstance(expected,str):raise ValueError("Use the study-specific verifier for this manifest schema")
        if sha(directory/name)!=expected:raise AssertionError("Artifact differs: "+str(directory/name))
        checked+=1
    return checked


def git_bytes(*args):return subprocess.check_output(["git",*args],cwd=ROOT)


def run(output):
    if output.exists():raise FileExistsError(output)
    standard={}
    for name in ("gating_audit","bilinear_study","interdiction_audit","projection_repeated","falsification_controls","legacy_statistics_audit"):
        directory=RESULTS/name
        if (directory/"manifest.json").exists():standard[name]={"hashed_files_checked":simple_manifest(directory),"manifest_sha256":sha(directory/"manifest.json")}
    for name,key in (("confirmation","result_sha256"),("robustness","artifact_sha256")):
        directory=RESULTS/name;manifest=json.loads((directory/"manifest.json").read_text());count=0
        for filename,expected in manifest[key].items():
            if sha(directory/filename)!=expected:raise AssertionError("Frozen original study differs")
            count+=1
        if name=="confirmation":
            for filename,expected in manifest["sha256"].items():
                if sha(ROOT/filename)!=expected:raise AssertionError("Frozen source/original input differs")
                count+=1
        standard[name]={"hashed_files_checked":count,"manifest_sha256":sha(directory/"manifest.json")}
    matrices={}
    for directory in sorted(DATA.iterdir()):
        if not directory.is_dir() or not (directory/"protocol.json").exists() or not (directory/"sources").exists():continue
        protocol=json.loads((directory/"protocol.json").read_text())
        for name,expected in protocol["source_sha256"].items():
            if sha(directory/"sources"/Path(name).name)!=expected:raise AssertionError("Frozen matrix source differs")
        trials=[p for p in sorted(directory.glob("r*")) if p.is_dir() and (p/"manifest.json").exists()]
        matrices[directory.name]={"trials_with_manifests":len(trials),"hashed_files_checked":sum(simple_manifest(p) for p in trials),
                                 "protocol_sha256":sha(directory/"protocol.json")}
    generated={}
    for path in sorted((ROOT/"manuscript/generated").glob("*_manifest.json")):
        manifest=json.loads(path.read_text());table=path.with_name(path.name.replace("_manifest.json",".tex"))
        if sha(table)!=manifest["output_sha256"]:raise AssertionError("Generated table differs: "+str(table))
        generator=ROOT/"manuscript/scripts"/("generate_"+table.stem+".py")
        if sha(generator)!=manifest["source_sha256"]:raise AssertionError("Table generator differs")
        inputs=manifest.get("input_sha256")
        if isinstance(inputs,dict):
            for name,expected in inputs.items():
                if sha(ROOT/name)!=expected:raise AssertionError("Table input differs")
        elif table.stem=="gating_evidence":
            if sha(RESULTS/"gating_audit_verification.json")!=inputs:raise AssertionError("Gating verification input differs")
        elif table.stem=="projection_evidence":
            if sha(RESULTS/"projection_repeated/manifest.json")!=inputs:raise AssertionError("Projection input differs")
        elif table.stem=="bilinear_evidence":
            if sha(RESULTS/"bilinear_study_verification.json")!=manifest["verification_sha256"]:raise AssertionError("Bilinear verification input differs")
        generated[table.name]=sha(table)
    base="cc707b3"  # Accepted manuscript before this research continuation.
    style={}
    for name in ("manuscript/manuscript.sty","manuscript/compile.sh"):
        style[name]=git_bytes("show",base+":"+name)==(ROOT/name).read_bytes()
    original_main=git_bytes("show",base+":manuscript/main.tex").decode();current_main=(ROOT/"manuscript/main.tex").read_text()
    for key,pattern in (("document_class",r"^\\documentclass.*$"),("title",r"^\\title.*$")):
        style[key]=re.findall(pattern,original_main,re.M)==re.findall(pattern,current_main,re.M)
    original_sections=[];current_sections=[]
    for path in sorted((ROOT/"manuscript/sections").glob("0*.tex")):
        original=git_bytes("show",base+":"+str(path.relative_to(ROOT))).decode()
        original_sections+=re.findall(r"^\\section\{([^\n]+)",original,re.M)
        current_sections+=re.findall(r"^\\section\{([^\n]+)",path.read_text(),re.M)
    style["seven_main_section_titles"]=original_sections==current_sections and len(current_sections)==7
    style["original_static_implementation_files"]=not bool(git_bytes("diff","--name-only",base,"--","thesis_research/src/phase2_certgraph").strip())
    style["tracked_existing_figures"]=not bool(git_bytes("diff","--name-only",base,"--","manuscript/figures","thesis_paper/figures").strip())
    if not all(style.values()):raise AssertionError("Original design/source preservation check failed: "+str(style))
    private_paths=[];private_headers=[];credential_matches=[]
    private_file=Path("/tmp/goad-q1-independent-2019/credentials.json")
    credentials=list(json.loads(private_file.read_text()).values()) if private_file.exists() else []
    for path in DATA.rglob("*"):
        if not path.is_file():continue
        if path.suffix.casefold() in (".pfx",".p12",".ccache",".kirbi",".key"):private_paths.append(str(path.relative_to(ROOT)))
        content=path.read_bytes()
        if any(token in content for token in (b"-----BEGIN PRIVATE KEY-----",b"-----BEGIN RSA PRIVATE KEY-----")):private_headers.append(str(path.relative_to(ROOT)))
        if any(value.encode() in content for value in credentials):credential_matches.append(str(path.relative_to(ROOT)))
    if private_paths or private_headers or credential_matches:raise AssertionError("Private material in new live dataset")
    log=(ROOT/"research_notes/2026-11-10/continued_tests.log").read_text();counts=re.findall(r"Ran (\d+) tests",log)
    tests={"count":int(counts[-1]) if counts else None,"status":"passed" if re.search(r"\nOK\s*$",log) else "not_verified","log_sha256":sha(ROOT/"research_notes/2026-11-10/continued_tests.log")}
    if tests["status"]!="passed":raise AssertionError("Latest test log not passing")
    result={"checked_utc":datetime.now(timezone.utc).isoformat(),"workspace":str(ROOT),"status":"passed","standard_studies":standard,
        "live_matrices":matrices,"generated_tables":generated,"preservation_from_commit":base,"preservation":style,
        "new_dataset_privacy":{"private_artifact_paths":private_paths,"private_key_headers":private_headers,"credential_value_matches":credential_matches,
                               "credential_scan_performed":bool(credentials)},"unit_tests":tests,"current_manuscript_pdf_sha256":sha(ROOT/"manuscript/main.pdf"),
        "scope":"Local artifact/style/privacy integrity; use independent study reports for scientific outcome checks; no acceptance or public-release certification",
        "audit_source_sha256":sha(Path(__file__))}
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");output.with_suffix(".source.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps({"status":result["status"],"studies":len(standard),"matrices":len(matrices),"unit_tests":tests["count"],"preservation":style},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);args=p.parse_args();run(args.output)
