"""Collect a later CA read-only export and audit explicitly supplemented views.

Original captures and manifests remain unchanged. Only missing CA exports are
supplied, in an ephemeral copy, from a separately hashed later observation.
The later snapshot is not evidence of a past template state or clock ordering.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

from .independent_policy_2019 import IndependentRunner
from .adjudicate_policy_matrix import run as adjudicate
from .evaluate_live_identity import run as identity
from .verify_paired_policy import verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")


def capture(output):
    output.mkdir(parents=True, exist_ok=False)
    runner = IndependentRunner(SimpleNamespace(output=output))
    runner.ps(runner.admin, "context", """$d=Get-ADDomain
if($d.DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
@{domain=$d.DNSRoot;domain_sid=$d.DomainSID.Value;computer=$env:COMPUTERNAME;ca='Q1-Evidence-CA';utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress""")
    script = """if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
certutil.exe -config ($env:COMPUTERNAME+'.q1lab.test\\Q1-Evidence-CA') -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv
if($LASTEXITCODE -ne 0){throw 'CA export failed'}
exit 0"""
    (output/"public_export.ps1").write_text(script)
    runner.ps(runner.admin, "ca_export", script)
    (output/"execution_source.py").write_bytes(Path(__file__).read_bytes())
    dump(output/"scope.json", {"collected_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Later read-only CA database export; not a contemporaneous trial observation or evidence of past policy state"})
    dump(output/"manifest.json", {p.name: sha(p) for p in output.iterdir() if p.is_file()})


@contextmanager
def evidence_view(matrix, supplement):
    manifest = json.loads((supplement/"manifest.json").read_text())
    for name, expected in manifest.items():
        if sha(supplement/name) != expected:
            raise ValueError("Supplement hash mismatch: "+name)
    export = json.loads((supplement/"ca_export.json").read_text())
    if export["returncode"] != 0:
        raise ValueError("Supplement export failed")
    context = json.loads(json.loads((supplement/"context.json").read_text())["stdout"])
    supplemented = []
    with tempfile.TemporaryDirectory(prefix="goad-q1-evidence-view-") as temporary:
        view = Path(temporary)/"matrix"
        shutil.copytree(matrix, view)
        for trial in sorted(view.glob("r*")):
            if not (trial/"manifest.json").exists():
                continue
            original_manifest = json.loads((trial/"manifest.json").read_text())
            for name, expected in original_manifest.items():
                if sha(trial/name) != expected:
                    raise ValueError("Original trial hash mismatch: "+trial.name+"/"+name)
            local = json.loads(json.loads((trial/"00_domain_context.json").read_text())["stdout"])
            if (local["dns_root"] != context["domain"] or local["domain_sid"] != context["domain_sid"]
                    or local["computer"] != context["computer"] or local["ca_name"] != context["ca"]):
                raise ValueError("Supplement and trial belong to different CA/forest")
            destination = trial/"99_ca_bridge.json"
            if not destination.exists():
                shutil.copyfile(supplement/"ca_export.json", destination)
                original_manifest[destination.name] = sha(destination)
                dump(trial/"manifest.json", original_manifest)
                supplemented.append(trial.name)
        yield view, supplemented


def review(matrix, supplement, output):
    output.mkdir(parents=True, exist_ok=False)
    with evidence_view(matrix, supplement) as (view, supplied):
        adjudicate(view, output/"adjudication.json")
        verify(view, output/"adjudication.json", output/"contrasts.json")
        identity(view, output/"adjudication.json", output/"identity.json")
    dump(output/"provenance.json", {"original_matrix": str(matrix), "supplement": str(supplement),
        "supplemented_missing_ca_exports": supplied,
        "original_trial_manifest_sha256": {p.parent.name: sha(p) for p in sorted(matrix.glob("r*/manifest.json"))},
        "supplement_manifest_sha256": sha(supplement/"manifest.json"),
        "scope": "Original per-trial exports used where available; missing exports supplied by later read-only CA snapshot in ephemeral copies. No original evidence or manifest modified. Later snapshot cannot establish historical policy or temporal causality."})
    (output/"execution_source.py").write_bytes(Path(__file__).read_bytes())
    dump(output/"manifest.json", {p.name: sha(p) for p in output.iterdir() if p.is_file()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="action", required=True)
    c = commands.add_parser("capture"); c.add_argument("output", type=Path)
    r = commands.add_parser("review")
    for name in ("matrix", "supplement", "output"):
        r.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.action == "capture": capture(args.output)
    else: review(args.matrix, args.supplement, args.output)
