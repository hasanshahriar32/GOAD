"""Paired ESC13 abstraction evaluation and measured screening/verification cost.
Every counterfactual family is confined to one split. Saved predictions include
family IDs so intervals and paired analyses use families rather than rows.
"""
import argparse,gzip,json,time,statistics,pickle
from pathlib import Path
from collections import defaultdict
import numpy as np
import torch
from sklearn.ensemble import RandomForestClassifier
from common import ROOT,environment,write_json,assert_disjoint,fingerprint,bootstrap_interval
from learning import fit_gnn,fit_mlp,predict_gnn,metrics
from esc13_cases import make_split,to_pyg,reference,independent_reference,tabular_features,MUTATIONS

def necessary_flags(case):
    auth,approval,sig,_=case['features']['Template'][case['target_template']]
    return bool(auth and not approval and not sig)

def timed(fn,repeats=5):
    fn();ts=[]
    for _ in range(repeats):
        t=time.perf_counter();fn();ts.append((time.perf_counter()-t)*1000)
    return {'median_ms':statistics.median(ts),'min_ms':min(ts),'max_ms':max(ts),'repeats':repeats}

def describe(cases,p):
    y=[reference(c) for c in cases];out=metrics(y,p,2);pred=p.argmax(1)
    family_correct=defaultdict(list)
    for c,z,v in zip(cases,pred,y):family_correct[c['family']].append(int(z==v))
    complete=[int(all(v)) for v in family_correct.values()]
    out['pair_both_correct']=float(np.mean(complete))
    out['pair_both_correct_ci95']=bootstrap_interval(complete)
    out['by_intervention']={}
    for mutation in MUTATIONS:
        ix=[i for i,c in enumerate(cases) if c['mutation']==mutation]
        if ix:out['by_intervention'][mutation]=metrics(np.array(y)[ix],p[ix],2)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,nargs='+',default=[11,29,47]);ap.add_argument('--epochs',type=int,default=80)
    ap.add_argument('--output',type=Path,default=ROOT/'thesis_research/results/publication_validation/counterfactual')
    args=ap.parse_args();torch.set_num_threads(2);args.output.mkdir(parents=True,exist_ok=True)
    result={'scope':'Fully observed effective-permission abstraction of ESC13 prerequisites; not Windows exploit validation.',
       'config':{'seeds':args.seeds,'epochs':args.epochs,'train_families':300,'validation_families':100,'test_families':150,
                 'depths_train':[0,1,2,3],'depths_long':[5,6,7,8],'screen_selection':'min positive validation probability; no test tuning'},
       'environment':environment(),'runs':[]}
    for seed in args.seeds:
        print(f'Counterfactual seed={seed}',flush=True)
        cases={'train':make_split('cf-v1-train',seed,300),'validation':make_split('cf-v1-validation',seed,100),
               'iid':make_split('cf-v1-iid',seed,150),
               'long_paths':make_split('cf-v1-long',seed,150,depths=(5,6,7,8)),
               'larger_graphs':make_split('cf-v1-large',seed,150,extra=(128,256)),
               'remote_membership':make_split('cf-v1-remote',seed,100,depths=(5,6,7,8),mutations=['membership'])}
        splits={name:[to_pyg(c) for c in cs] for name,cs in cases.items()}
        checks=assert_disjoint(splits)
        # Differential oracle testing on ALL dataset cases, before model training.
        for name,cs in cases.items():
            for c in cs:
                if reference(c)!=independent_reference(c):raise AssertionError(f'oracle disagreement: {c["family"]}')
        with gzip.open(args.output/f'{seed}_cases.json.gz','wt') as f:json.dump(cases,f)
        write_json(args.output/f'{seed}_manifest.json',[
            {'split':name,'family':c['family'],'variant':c['variant'],'mutation':c['mutation'],'depth':c['depth'],
             'label':reference(c),'input_hash':fingerprint(d,t)}
            for name,cs in cases.items() for c,(d,_,t) in zip(cs,splits[name])])
        model,training=fit_gnn(splits['train'],splits['validation'],2,seed,epochs=args.epochs)
        write_json(args.output/f'{seed}_training.json',training)
        torch.save({'state_dict':model.state_dict(),'metadata':splits['train'][0][0].metadata(),'selected_epoch':training['selected_epoch']},args.output/f'{seed}_gnn.pt')
        predictors={'CertGraph':lambda name:predict_gnn(model,splits[name])}
        ytrain=[reference(c) for c in cases['train']];yval=[reference(c) for c in cases['validation']]
        for structural,name in [(False,'Feature MLP'),(True,'Graph-count MLP')]:
            pred,checkpoint=fit_mlp([tabular_features(c,structural) for c in cases['train']],ytrain,
                                   [tabular_features(c,structural) for c in cases['validation']],yval,2,seed)
            predictors[name]=lambda split,pred=pred,s=structural:pred([tabular_features(c,s) for c in cases[split]])
            torch.save(checkpoint,args.output/f'{seed}_{name.replace(" ","_")}.pt')
        rf=RandomForestClassifier(n_estimators=200,random_state=seed,n_jobs=2)
        rf.fit([tabular_features(c,True) for c in cases['train']],ytrain)
        predictors['Graph-count RF']=lambda name:rf.predict_proba([tabular_features(c,True) for c in cases[name]])
        with (args.output/f'{seed}_rf.pkl').open('wb') as f:pickle.dump(rf,f)
        thresholds={name:float(pred('validation')[np.array(yval)==1,1].min()) for name,pred in predictors.items()}
        run={'seed':seed,'split_check':checks,'oracle_agreement':True,'selected_epoch':training['selected_epoch'],
             'validation_screen_thresholds':thresholds,'test_sets':{}}
        for split in ['iid','long_paths','larger_graphs','remote_membership']:
            cs=cases[split];truth=np.array([reference(c) for c in cs]);probs={name:pred(split) for name,pred in predictors.items()}
            probs['Symbolic reference']=np.eye(2)[truth]
            metrics_by_model={name:describe(cs,p) for name,p in probs.items()}
            hybrid={}
            timings={'Symbolic reference':timed(lambda:[reference(c) for c in cs]),
                     'Necessary flags + reference':timed(lambda:[reference(c) if necessary_flags(c) else 0 for c in cs])}
            for name,pred in predictors.items():
                selected=probs[name][:,1]>=thresholds[name]
                hp=np.eye(2)[truth*selected.astype(int)]
                hybrid[name]={'threshold':thresholds[name],'candidates':int(selected.sum()),
                              'candidate_fraction':float(selected.mean()),**describe(cs,hp)}
                def pipeline(pred=pred,threshold=thresholds[name]):
                    chosen=pred(split)[:,1]>=threshold
                    return [reference(c) if keep else 0 for c,keep in zip(cs,chosen)]
                timings[name+' + reference']=timed(pipeline,repeats=3)
            timings['scope']='Repeated in-memory corpus microbenchmark; includes model batching or feature extraction and selected checks; excludes raw collector ingestion. Shared CPU with other local processes.'
            write_json(args.output/f'{seed}_{split}_predictions.json',[
                {'family':c['family'],'variant':c['variant'],'mutation':c['mutation'],'depth':c['depth'],'label':int(truth[i]),
                 'scores':{name:float(p[i,1]) for name,p in probs.items()}}
                for i,c in enumerate(cs)])
            run['test_sets'][split]={'models':metrics_by_model,'hybrid':hybrid,'timings':timings}
            print(split,{name:round(m['accuracy'],3) for name,m in metrics_by_model.items()},flush=True)
        result['runs'].append(run);write_json(args.output/'results.json',result)
    write_json(args.output/'results.json',result)
if __name__=='__main__':main()
