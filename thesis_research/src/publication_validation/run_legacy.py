"""Independent holdouts and fair baselines on the legacy seven-class generator.
Original JSON results are never overwritten. This remains synthetic research.
"""
import argparse, json, time
from pathlib import Path
import numpy as np
import torch
from sklearn.ensemble import RandomForestClassifier
from common import ROOT, environment, fingerprint, assert_disjoint, write_json
from learning import fit_gnn, predict_gnn, fit_mlp, metrics
from generator import generate_dataset, CLASS_TO_IDX
from train import extract_graph_counts
from legacy_rules import GeneratorRuleBaseline
from bfs_baseline import BloodHoundBFSBaseline

def features(samples,augmented):
    return np.array([d['Template'].x[t].tolist()+(extract_graph_counts(d,t) if augmented else []) for d,_,t in samples])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,nargs='+',default=[11,29,47]);ap.add_argument('--epochs',type=int,default=80)
    ap.add_argument('--output',type=Path,default=ROOT/'thesis_research/results/publication_validation/legacy')
    args=ap.parse_args();torch.set_num_threads(2);args.output.mkdir(parents=True,exist_ok=True)
    result={'scope':'Synthetic legacy-generator audit; local symbolic surrogates are not commercial tools.',
            'config':{'seeds':args.seeds,'epochs':args.epochs,'train_n':700,'validation_n':210,'test_n':350},
            'environment':environment(),'runs':[]}
    for seed in args.seeds:
        for condition in ['mixed_training','no_hn_training']:
            print(f'Legacy seed={seed}, condition={condition}',flush=True)
            raw={split:generate_dataset(n,seed=seed,namespace=f'publication-legacy-v1:{condition}:{split}',
                include_hard_negatives=(condition=='mixed_training' if split!='test' else True))
                for split,n in [('train',700),('validation',210),('test',350)]}
            disjoint=assert_disjoint(raw)
            manifest=[{'split':split,'input_hash':fingerprint(d,t),'label':c,'target':t}
                      for split,ss in raw.items() for d,c,t in ss]
            prefix=f'{seed}_{condition}'
            write_json(args.output/(prefix+'_manifest.json'),manifest)
            data={k:[(d,CLASS_TO_IDX[c],t) for d,c,t in v] for k,v in raw.items()}
            train,val,test=data['train'],data['validation'],data['test']
            y=[s[1] for s in test]; hn=[i for i,(d,c,t) in enumerate(raw['test']) if c=='Safe' and any(d['Template'].x[t,j]==1 for j in [0,7,8])]
            predictions={};timings={};records={}
            start=time.perf_counter()
            model,training=fit_gnn(train,val,7,seed,epochs=args.epochs)
            start_pred=time.perf_counter();predictions['CertGraph']=predict_gnn(model,test);timings['CertGraph']=time.perf_counter()-start_pred
            torch.save({'model_state_dict':model.state_dict(),'seed':seed,'condition':condition,'selection':'validation_nll',
                        'architecture':{'hidden':32,'out':16,'heads':4,'classes':7}},args.output/(prefix+'_gnn.pt'))
            write_json(args.output/(prefix+'_training.json'),training)
            for augmented,name in [(False,'Feature MLP'),(True,'Graph-count MLP')]:
                predict,checkpoint=fit_mlp(features(train,augmented),[s[1] for s in train],
                    features(val,augmented),[s[1] for s in val],7,seed)
                begin=time.perf_counter();predictions[name]=predict(features(test,augmented));timings[name]=time.perf_counter()-begin
                torch.save(checkpoint,args.output/(prefix+('_augmlp.pt' if augmented else '_mlp.pt')))
            forest=RandomForestClassifier(n_estimators=200,random_state=seed,n_jobs=2)
            forest.fit(features(train,True),[s[1] for s in train])
            begin=time.perf_counter();predictions['Graph-count RF']=forest.predict_proba(features(test,True));timings['Graph-count RF']=time.perf_counter()-begin
            import pickle
            with (args.output/(prefix+'_rf.pkl')).open('wb') as f:pickle.dump(forest,f)
            for name,rule in [('Generator diagnostic',GeneratorRuleBaseline()),('Legacy direct-edge rules',BloodHoundBFSBaseline())]:
                begin=time.perf_counter();preds=rule.predict(raw['test']);timings[name]=time.perf_counter()-begin
                predictions[name]=np.eye(7)[preds]
            for name,p in predictions.items():
                m=metrics(y,p,7);m['hard_negative_n']=len(hn)
                m['hard_negative_specificity']=float((p.argmax(1)[hn]==CLASS_TO_IDX['Safe']).mean()) if hn else None
                m['single_pass_test_seconds']=timings[name]
                records[name]=m
            write_json(args.output/(prefix+'_predictions.json'),[
                {'input_hash':fingerprint(d,t),'label':int(c),'hard_negative':i in hn,
                 'probabilities':{k:[float(x) for x in p[i]] for k,p in predictions.items()}}
                for i,(d,c,t) in enumerate(test)])
            result['runs'].append({'seed':seed,'condition':condition,'split_check':disjoint,'selected_epoch':training['selected_epoch'],
                'models':records,'seconds':time.perf_counter()-start})
            write_json(args.output/'results.json',result)
            print({n:round(m['macro_f1'],4) for n,m in records.items()},flush=True)
    write_json(args.output/'results.json',result)
if __name__=='__main__':main()
