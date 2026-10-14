"""Recompute saved aggregate metrics from per-case predictions and audit splits."""
import gzip,json
from collections import defaultdict
import numpy as np
from common import ROOT,write_json
from learning import metrics
from esc13_cases import reference

BASE=ROOT/'thesis_research/results/publication_validation'

def close(a,b):
    if a is None or b is None:assert a is b
    else:assert np.allclose(a,b,atol=1e-10,rtol=1e-10),(a,b)

def main():
    report={'legacy_runs':0,'counterfactual_runs':0,'prediction_sets_checked':0,'case_rows_checked':0}
    for kind in ['legacy','counterfactual']:
        result=json.loads((BASE/kind/'results.json').read_text())
        expected=6 if kind=='legacy' else 3
        assert len(result['runs'])==expected
        for run in result['runs']:
            seed=run['seed'];prefix=f'{seed}_{run["condition"]}' if kind=='legacy' else str(seed)
            manifest=json.loads((BASE/kind/f'{prefix}_manifest.json').read_text())
            hashes=defaultdict(set);families=defaultdict(set)
            for row in manifest:
                hashes[row['split']].add(row['input_hash'])
                if 'family' in row:families[row['split']].add(row['family'])
            for mapping in [hashes,families]:
                for a in mapping:
                    for b in mapping:
                        if a!=b:assert not mapping[a]&mapping[b],(kind,prefix,a,b)
            history=json.loads((BASE/kind/f'{prefix}_training.json').read_text())
            # Account for the explicit 1e-6 improvement tolerance.
            chosen=next(h['validation_nll'] for h in history['history'] if h['epoch']==history['selected_epoch'])
            assert chosen<=min(h['validation_nll'] for h in history['history'])+1.01e-6
            splits=['test'] if kind=='legacy' else list(run['test_sets'])
            if kind=='counterfactual':
                with gzip.open(BASE/kind/f'{seed}_cases.json.gz','rt') as f:cases=json.load(f)
                for name,cs in cases.items():
                    saved={(r['family'],r['variant']):r['label'] for r in manifest if r['split']==name}
                    for c in cs:assert reference(c)==saved[c['family'],c['variant']]
            for split in splits:
                filename=f'{prefix}_predictions.json' if kind=='legacy' else f'{seed}_{split}_predictions.json'
                rows=json.loads((BASE/kind/filename).read_text());y=[r['label'] for r in rows]
                models=run['models'] if kind=='legacy' else run['test_sets'][split]['models']
                for name,record in models.items():
                    p=np.array([r['probabilities'][name] for r in rows]) if kind=='legacy' else np.array([[1-r['scores'][name],r['scores'][name]] for r in rows])
                    computed=metrics(y,p,7 if kind=='legacy' else 2)
                    for key in computed:close(computed[key],record[key])
                    if kind=='counterfactual':
                        pairs=defaultdict(list)
                        for r,pred in zip(rows,p.argmax(1)):pairs[r['family']].append(int(r['label']==pred))
                        assert all(len(pair)==2 for pair in pairs.values())
                        close(np.mean([all(pair) for pair in pairs.values()]),record['pair_both_correct'])
                    else:
                        ix=[i for i,r in enumerate(rows) if r['hard_negative']]
                        # Safe index is recovered from saved generator label ordering.
                        from generator import CLASS_TO_IDX
                        close((p.argmax(1)[ix]==CLASS_TO_IDX['Safe']).mean(),record['hard_negative_specificity'])
                if kind=='counterfactual':
                    for name,record in run['test_sets'][split]['hybrid'].items():
                        selected=np.array([r['scores'][name]>=record['threshold'] for r in rows])
                        hp=np.eye(2)[np.array(y)*selected]
                        for key,value in metrics(y,hp,2).items():close(value,record[key])
                        close(selected.mean(),record['candidate_fraction'])
                report['prediction_sets_checked']+=1;report['case_rows_checked']+=len(rows)
            report[kind+'_runs']+=1
    report['status']='passed';write_json(BASE/'integrity_report.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
