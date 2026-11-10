"""Read-only live regression control for the empty-System-export collector fix."""
from pathlib import Path
from types import SimpleNamespace
import json

from ..independent_policy_2019 import IndependentRunner, system_export_script
from ..supplement_matrix_evidence import dump, sha


def run():
    output=Path("thesis_research/data/lineage_live/2026-11-10/current_patch_export_control_01")
    output.mkdir(parents=True,exist_ok=False)
    runner=IndependentRunner(SimpleNamespace(output=output))
    boundary=runner.ps(runner.admin,"boundary","if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong forest'};(Get-WinEvent -LogName System -MaxEvents 1).RecordId")
    script=system_export_script(int(boundary["stdout"].strip()))
    (output/"empty_export.ps1").write_text(script)
    result=runner.ps(runner.admin,"empty_export",script)
    if result["stdout"].strip():raise ValueError("Control interval was not empty")
    runner.ps(runner.admin,"subsequent_ca_export","certutil.exe -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv;if($LASTEXITCODE -ne 0){throw 'CA export failed'};exit 0")
    (output/"execution_source.py").write_bytes(Path(__file__).read_bytes())
    from .. import independent_policy_2019
    (output/"collector_source.py").write_bytes(Path(independent_policy_2019.__file__).read_bytes())
    dump(output/"result.json",{"status":"passed","scope":"Actual empty KDC System interval returns zero and permits subsequent read-only CA export; no intervention trial rerun"})
    dump(output/"manifest.json",{p.name:sha(p) for p in output.iterdir() if p.is_file()})
    print(json.dumps({"status":"passed"}))


if __name__=="__main__":run()
