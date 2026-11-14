"""Render equal-input, prospective-transfer and measured-cost evidence."""
import hashlib
import json
from pathlib import Path
from evidence_table_layout import style_evidence_tables
from generate_lineage_evidence import table

ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/'thesis_research/results/lineage_constraints/2026-11-10'
DATA=ROOT/'thesis_research/data/lineage_live/2026-11-10'


def main():
    paths=[RESULTS/'sql_comparison/results.json',RESULTS/'sql_comparison_verification.json',RESULTS/'transfer_workload_01_external_final.json',
           RESULTS/'transfer_workload_01_verification_complete.json',RESULTS/'transfer_workload_01_identity_final.json',
           DATA/'collection_pilot_02/results.json',RESULTS/'collection_pilot_02_verification.json']
    sql,verified,external,transfer,identity,pilot,pilot_verified=[json.loads(p.read_text()) for p in paths]
    assert verified['status']==transfer['status']==pilot_verified['status']=='passed'
    rows=[]
    for key,label in [('constraint_identity','CIPG identity'),('sql_strong_join','SQL strong join'),('sql_guarded','SQL guarded')]:
        r=sql['by_group_method']['main/'+key];rows.append([label,r['resolved'],r['correct_certain'],r['wrong_certain'],r['candidate_retained']])
    text=table('Equal-input identity projection on 1,410 main challenge histories, including 60 chronology-negative controls; 1,241 true successful observed links. All event times are erased. The 60 wrong terminal claims in each row are the chronology controls. A separate 60 consistently forged-source controls also fool every method. This compares relational identity contracts, not full PIDS detection.',
        'tab:sql_identity','lrrrr','Method & Resolved & Correct & Wrong & True candidates retained',rows)
    labels=json.loads((RESULTS/'transfer_workload_01_adjudication_final.json').read_text())['trials']
    paths.append(RESULTS/'transfer_workload_01_adjudication_final.json');rows=[]
    for condition,label in [('baseline','Baseline'),('enabled','Enabled'),('rollback_first','Rollback first')]:
        r=external['by_condition'][condition]
        selected=[entry for entry in labels if entry['condition'].startswith('transfer_'+condition+'_')]
        self_count=sum(entry['observed_outcome']=='self_certificate_use' for entry in selected)
        admin_count=sum(entry['successful_administrator_use'] for entry in selected)
        assert admin_count==r['verified_administrative_cases']
        rows.append([label,r['certificate_cases'],self_count,admin_count,r['certipy_pre_esc1'],r['certipy_post_esc1'],r['sigma_eku_rule']])
    text+=table('Prospective transfer to a new forest/CA, two templates and two ordinary enrollers: six concurrent batches and 24 distinct certificates. Each condition has four template/batch/enroller units shared by eight certificate cases. ESC1 and Sigma columns count these four configuration units; they are not attack-detection counts. The Windows image family is shared with the previous environment.',
        'tab:transfer_workload','lrrrrrr','Condition & Cases & Self & Admin & ESC1 pre & ESC1 post & Risky EKU',rows)
    rows=[]
    for r in pilot['arms']:
        rows.append([r['pair'],r['arm'],r['raw_successful_exact_certificate_kdc_records'],f"{1000*r['median_authentication_seconds']:.1f}",
                     f"{1000*r['python_process_cpu_seconds']:.1f}",f"{r['collector_rss_peak_kib']/1024:.1f}"])
    text+=table('Paired isolated-lab pilot: eight authentications per arm, three seeded arm orders. Auth denotes the median host Certipy process envelope in milliseconds; CPU is Python process CPU time during the arm, also milliseconds. RSS is sampled Python collector MiB, excluding Certipy children and the Windows VM. Outcome-verification waits occur after the measured arm.',
        'tab:collection_pilot','rlrrrr','Pair & Arm & Verified uses & Auth ms & CPU ms & RSS MiB',rows)
    path=ROOT/'manuscript/generated/gap_closure_evidence.tex';path.write_text(style_evidence_tables(text))
    path.with_name('gap_closure_evidence_manifest.json').write_text(json.dumps({"layout_sha256": hashlib.sha256((Path(__file__).parent/"evidence_table_layout.py").read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},indent=2)+'\n')


if __name__=='__main__':main()
