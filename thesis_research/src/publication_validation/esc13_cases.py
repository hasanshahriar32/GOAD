"""Paired principal-specific ESC13 prerequisite benchmark.

Scope: a *fully observed abstract model*, not a Windows exploitability oracle.
ACL edges denote collector-resolved effective allow grants; deny precedence,
SID filtering, KDC/patch behavior, enrollment-agent and relay mechanics are not
modeled. Policy groups are assumed eligible (empty universal security groups).
CA.trusted denotes resolved trust/availability prerequisites. Labels are derived
from the reference evaluator, never supplied as GNN input features.
"""
import copy, hashlib, random
from collections import deque
import numpy as np
import torch
from torch_geometric.data import HeteroData

MUTATIONS=['membership','template_acl','ca_acl','publication','authentication',
           'approval','signature','policy_link','privilege','ca_trust']
# All cases share this metadata; missing edge relations remain empty tensors.
RELATIONS=[('User','member_of','Group'),('Group','member_of','Group'),
           ('Group','enrolls','Template'),('User','enrolls','CA'),
           ('Template','published_to','CA'),('Template','has_policy','Policy'),
           ('Policy','linked_group','Group')]
FEATURES={'User':['focal'], 'Group':['highvalue'],
          'Template':['authentication','approval_required','signature_required','focal'],
          'CA':['trusted'], 'Policy':['present']}

def make_family(namespace,seed,family,depth,extra_groups=16,mutation='membership'):
    rng=random.Random(int.from_bytes(hashlib.sha256(f'{namespace}:{seed}:{family}'.encode()).digest()[:8],'big'))
    # Two symmetric chains. Only chain A can enroll target T; chain B can enroll
    # distractor T. Swapping the users preserves all per-type degree counts.
    length=depth+1
    ag=list(range(length));bg=list(range(length,2*length));hv=2*length
    n=2*length+1+extra_groups
    c={'features':{'User':[[1.],[0.]], 'Group':[[float(i==hv)] for i in range(n)],
         'Template':[[1.,0.,0.,1.],[1.,0.,0.,0.]],'CA':[[1.]],'Policy':[[1.]]},
       'edges':{'|'.join(e):[] for e in RELATIONS},'focal_user':0,'target_template':0}
    def put(rel,edges):c['edges']['|'.join(rel)]=edges
    put(RELATIONS[0],[[0,ag[0]],[1,bg[0]]])
    links=[[a,b] for chain in [ag,bg] for a,b in zip(chain,chain[1:])]
    # Background component contains optional cycles but cannot bypass test chains.
    noise=list(range(hv+1,n))
    for a in noise:
        if len(noise)>1:
            b=rng.choice([x for x in noise if x!=a]);links.append([a,b])
        if rng.random()<.2 and len(noise)>2:
            b=rng.choice([x for x in noise if x!=a]);links.append([a,b])
    put(RELATIONS[1],sorted(set(map(tuple,links))))
    put(RELATIONS[2],[[ag[-1],0],[bg[-1],1]])
    put(RELATIONS[3],[[0,0],[1,0]])
    put(RELATIONS[4],[[0,0],[1,0]])
    put(RELATIONS[5],[[0,0],[1,0]])
    put(RELATIONS[6],[[0,hv]])
    # Shared permutation across the pair removes index conventions.
    negative=copy.deepcopy(c)
    e=negative['edges'];f=negative['features']
    if mutation=='membership':e['|'.join(RELATIONS[0])]=[[0,bg[0]],[1,ag[0]]]
    elif mutation=='template_acl':e['|'.join(RELATIONS[2])]=[[ag[-1],1],[bg[-1],1]]
    elif mutation=='ca_acl':e['|'.join(RELATIONS[3])]=[[1,0]]
    elif mutation=='publication':e['|'.join(RELATIONS[4])]=[[1,0]]
    elif mutation=='authentication':f['Template'][0][0]=0.
    elif mutation=='approval':f['Template'][0][1]=1.
    elif mutation=='signature':f['Template'][0][2]=1.
    elif mutation=='policy_link':e['|'.join(RELATIONS[5])]=[[1,0]]
    elif mutation=='privilege':f['Group'][hv][0]=0.
    elif mutation=='ca_trust':f['CA'][0][0]=0.
    else:raise ValueError(mutation)
    maps={}
    for typ,features in c['features'].items():
        order=list(range(len(features)));rng.shuffle(order)
        maps[typ]={old:new for new,old in enumerate(order)}
    for case,variant in [(c,'positive'),(negative,'counterfactual')]:
        case['features']={typ:[values[old] for old,new in sorted(maps[typ].items(),key=lambda x:x[1])]
                          for typ,values in case['features'].items()}
        for key,edges in case['edges'].items():
            a,_,b=key.split('|');case['edges'][key]=sorted([[maps[a][i],maps[b][j]] for i,j in edges])
        case['focal_user']=maps['User'][0];case['target_template']=maps['Template'][0]
        case.update(family=f'{namespace}:{seed}:{family}',variant=variant,mutation=mutation,depth=depth)
    assert reference(c)==1 and reference(negative)==0
    return c,negative

def reached_groups(case):
    """Queue-based transitive group membership from the focal principal."""
    edges=case['edges'];u=case['focal_user'];adj={}
    for a,b in edges['Group|member_of|Group']:adj.setdefault(a,[]).append(b)
    q=deque(b for a,b in edges['User|member_of|Group'] if a==u);seen=set()
    while q:
        g=q.popleft()
        if g in seen:continue
        seen.add(g);q.extend(adj.get(g,[]))
    return seen

def reference(case):
    """Boolean reference query for the explicitly scoped abstract model."""
    f,e=case['features'],case['edges'];u,t=case['focal_user'],case['target_template']
    auth,approval,sigs,_=f['Template'][t]
    if not auth or approval or sigs:return 0
    members=reached_groups(case)
    if not any(g in members and v==t for g,v in e['Group|enrolls|Template']):return 0
    cas={c for v,c in e['Template|published_to|CA'] if v==t and f['CA'][c][0]}
    if not any(a==u and c in cas for a,c in e['User|enrolls|CA']):return 0
    policies={p for v,p in e['Template|has_policy|Policy'] if v==t and f['Policy'][p][0]}
    return int(any(p in policies and f['Group'][g][0] for p,g in e['Policy|linked_group|Group']))

def independent_reference(case):
    """Independent fixed-point/boolean-matrix evaluator for differential tests."""
    f=case['features'];e=case['edges'];u=case['focal_user'];t=case['target_template'];ng=len(f['Group'])
    closure=np.eye(ng,dtype=bool)
    for a,b in e['Group|member_of|Group']:closure[a,b]=True
    for k in range(ng):closure |= closure[:,k,None]&closure[None,k,:]
    member=np.zeros(ng,dtype=bool)
    for a,b in e['User|member_of|Group']:
        if a==u:member |= closure[b]
    enrollment=any(member[a] for a,b in e['Group|enrolls|Template'] if b==t)
    caok=any(a==u and (t,c) in set(map(tuple,e['Template|published_to|CA'])) and f['CA'][c][0] for a,c in e['User|enrolls|CA'])
    policyok=any((t,p) in set(map(tuple,e['Template|has_policy|Policy'])) and f['Policy'][p][0] and f['Group'][g][0] for p,g in e['Policy|linked_group|Group'])
    tf=f['Template'][t]
    return int(bool(enrollment and caok and policyok and tf[0] and not tf[1] and not tf[2]))

def to_pyg(case):
    d=HeteroData()
    for typ,values in case['features'].items():d[typ].x=torch.tensor(values,dtype=torch.float32)
    for a,r,b in RELATIONS:
        edges=case['edges']['|'.join((a,r,b))]
        ei=torch.tensor(edges,dtype=torch.long).t().contiguous() if edges else torch.empty((2,0),dtype=torch.long)
        d[a,r,b].edge_index=ei;d[b,'reverse_'+r,a].edge_index=ei.flip(0)
    return d,reference(case),case['target_template']

def tabular_features(case,structural=False):
    """Local attributes; augmented version adds direct graph counts, no closure."""
    t=case['target_template'];f=case['features'];e=case['edges']
    x=f['Template'][t][:3]
    if not structural:return x
    # All attributes + direct graph summaries; never an oracle label as a feature.
    x=x+[sum(v[0] for v in f['CA']),sum(v[0] for v in f['Group']),
        sum(b==t for a,b in e['Group|enrolls|Template']),
        sum(a==t for a,b in e['Template|published_to|CA']),
        sum(a==t for a,b in e['Template|has_policy|Policy']),
        sum(a==case['focal_user'] for a,b in e['User|enrolls|CA']),
        len(e['Policy|linked_group|Group']),len(e['Group|member_of|Group'])]
    return x

def make_split(namespace,seed,n_families,depths=(0,1,2,3),extra=(8,32),mutations=MUTATIONS):
    rng=random.Random(seed);cases=[]
    for i in range(n_families):
        pair=make_family(namespace,seed,i,rng.choice(depths),rng.randint(*extra),mutations[i%len(mutations)])
        cases.extend(pair)
    rng.shuffle(cases)
    return cases
