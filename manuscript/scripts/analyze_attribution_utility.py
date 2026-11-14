"""Exploratory ambiguity/decision-cost analysis of frozen confirmation predictions.

No new histories, training or deployment measurements. Loss is an explicit
illustrative decision model, not an elicited operational utility.
"""
import hashlib
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'thesis_research/results/lineage_constraints/2026-11-10/confirmation'
OUT = ROOT / 'manuscript/reviews/2026-11-14/research_revision/utility_analysis.json'

def analyze():
    labels = {r['case_id']: r for r in map(json.loads, (SOURCE / 'labels.jsonl').read_text().splitlines())
              if ':randomized_mix:' in r['case_id']}
    rows = list(map(json.loads, (SOURCE / 'predictions.jsonl').read_text().splitlines()))
    results = {}
    for method in sorted({r['method'] for r in rows}):
        selected = [r for r in rows if r['method'] == method and r['case_id'] in labels]
        assert len(selected) == len(labels) == 2000
        sizes, false_candidates, retained, tp, fp, true_overlap = [], 0, 0, 0, 0, 0
        for r in selected:
            label = labels[r['case_id']]
            possible = set(r['possible_issuance_ids'])
            truth = label['true_issuance_id']
            sizes.append(len(possible))
            false_candidates += len(possible - ({truth} if truth else set()))
            retained += bool(truth and truth in possible)
            target = bool(truth and label['true_exposure'])
            true_overlap += target
            claims = set(r['definite_exposure_ids'])
            tp += bool(target and truth in claims)
            fp += len(claims - ({truth} if target else set()))
        ordered = sorted(sizes)
        results[method] = dict(cases=len(selected), mean_candidates=mean(sizes),
            p95_candidates=ordered[(95*len(ordered)+99)//100-1], max_candidates=max(sizes),
            false_candidate_edges=false_candidates, true_candidates_retained=retained,
            true_overlap_edges=true_overlap, correct_definite_overlap_edges=tp,
            false_definite_overlap_edges=fp, unclaimed_true_overlap_edges=true_overlap-tp)
    a,b=results['constraint_lineage'],results['conjunctive_point']
    assert a['true_overlap_edges']==b['true_overlap_edges']==539
    delta_miss=a['unclaimed_true_overlap_edges']-b['unclaimed_true_overlap_edges']
    delta_false=b['false_definite_overlap_edges']-a['false_definite_overlap_edges']
    result=dict(scope='Exploratory reanalysis of 2000 frozen randomized histories; no enterprise prevalence inference',
        input_sha256={n:hashlib.sha256((SOURCE/n).read_bytes()).hexdigest() for n in ['labels.jsonl','predictions.jsonl']},
        methods=results, loss_model='L = unclaimed true overlap edges + r * false definite overlap edges',
        break_even_false_to_missed_cost=delta_miss/delta_false,
        cost_assumptions='Common unit costs, no review/time cost, no utility assigned to possible answers; illustrative only')
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    print(json.dumps(analyze(),indent=2))
