"""Measure captured collection-command envelopes and offline inference cost."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import time
import tracemalloc

from .evaluate_live_identity import identity_prediction


def summary(values):
    values=sorted(values)
    return {"n":len(values),"minimum":values[0],"median":statistics.median(values),"maximum":values[-1],"mean":statistics.mean(values)} if values else None


def run(matrix,output):
    if output.exists():raise FileExistsError(output)
    rows=[]
    for path in sorted(matrix.glob("r*")):
        if not (path/"manifest.json").exists():continue
        manifest=json.loads((path/"manifest.json").read_text())
        for name,expected in manifest.items():
            if hashlib.sha256((path/name).read_bytes()).hexdigest()!=expected:raise ValueError("Trial artifact differs")
        phases={};envelopes=[]
        for item in sorted(path.glob("*.json")):
            data=json.loads(item.read_text())
            if "host_before" not in data or "host_after" not in data:continue
            key=(data["host_before"],data["host_after"])
            # Effective-policy files duplicate an existing command result.
            if key in phases:continue
            phases[key]={"phase":item.name,"wall_seconds":data["host_after"]-data["host_before"],
                         "monotonic_seconds":data.get("host_monotonic_elapsed_ns",0)/1e9}
            envelopes.append(key)
        timings=[]
        for _ in range(10):
            before=time.perf_counter();predictions,records=identity_prediction(path);timings.append(time.perf_counter()-before)
        tracemalloc.start();identity_prediction(path);_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        rows.append({"trial":path.name,"recorded_command_envelope_seconds":max(e[1] for e in envelopes)-min(e[0] for e in envelopes),
            "logged_command_seconds":sum(r["monotonic_seconds"] for r in phases.values()),"phases":list(phases.values()),
            "offline_identity_seconds":summary(timings),"python_traced_peak_bytes":peak,"certificate_observations":records,
            "retained_raw_xml_bytes":(path/"events.xml").stat().st_size,"ca_export_bytes":(path/"99_ca_bridge.json").stat().st_size})
    result={"scope":"Measured experiment command envelopes and offline identity reasoning, not continuous polling, detection latency, host RSS or enterprise overhead",
        "trials":rows,"summary":{"trial_command_envelope_seconds":summary([r["recorded_command_envelope_seconds"] for r in rows]),
            "offline_identity_median_seconds":summary([r["offline_identity_seconds"]["median"] for r in rows]),
            "python_traced_peak_bytes":summary([r["python_traced_peak_bytes"] for r in rows])},
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_trial_manifest_sha256":{p.name:hashlib.sha256((p/"manifest.json").read_bytes()).hexdigest() for p in sorted(matrix.glob("r*")) if (p/"manifest.json").exists()}}
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result["summary"],indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("matrix",type=Path);p.add_argument("output",type=Path);args=p.parse_args();run(args.matrix,args.output)
