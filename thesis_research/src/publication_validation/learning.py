"""Fixed-budget training with validation-only checkpoint selection."""
import copy
import random
import time
import numpy as np
import torch
from torch_geometric.loader import DataLoader
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix, average_precision_score
from common import LEGACY
from model import CertGraph, MLPBaseline

def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

def prepare(samples):
    result=[]
    for d,y,t in samples:
        d=d.clone()
        d.target_idx=torch.tensor([t],dtype=torch.long)
        d.y_class=torch.tensor([int(y)],dtype=torch.long)
        result.append(d)
    return result

def predict_gnn(model,samples,batch_size=64):
    model.eval(); results=[]
    with torch.no_grad():
        for b in DataLoader(prepare(samples),batch_size=batch_size,shuffle=False):
            logits=model(b.x_dict,b.edge_index_dict)
            idx=b['Template'].ptr[:-1]+b.target_idx
            results.append(logits[idx].softmax(dim=1).cpu().numpy())
    return np.concatenate(results)

def fit_gnn(train,val,classes,seed,epochs=80,patience=15,skip=True):
    seed_all(seed)
    model=CertGraph(train[0][0].metadata(),hidden_channels=32,out_channels=16,
                    num_classes=classes,num_heads=4,dropout=.2,skip_connections=skip)
    model.eval()
    with torch.no_grad(): model(train[0][0].x_dict,train[0][0].edge_index_dict)
    opt=torch.optim.Adam(model.parameters(),lr=.005,weight_decay=1e-4)
    loader=DataLoader(prepare(train),batch_size=64,shuffle=True)
    best_loss=float('inf'); best_state=None; stale=0; history=[]; best_epoch=0
    start=time.perf_counter()
    for epoch in range(1,epochs+1):
        model.train(); total=0.
        for b in loader:
            opt.zero_grad(); logits=model(b.x_dict,b.edge_index_dict)
            idx=b['Template'].ptr[:-1]+b.target_idx
            loss=torch.nn.functional.cross_entropy(logits[idx],b.y_class)
            loss.backward(); opt.step(); total += loss.item()*b.num_graphs
        probs=predict_gnn(model,val)
        y=np.array([s[1] for s in val])
        vl=float(-np.log(np.maximum(probs[np.arange(len(y)),y],1e-12)).mean())
        history.append({'epoch':epoch,'train_loss':total/len(train),'validation_nll':vl})
        if vl < best_loss-1e-6:
            best_loss=vl;best_state=copy.deepcopy(model.state_dict());best_epoch=epoch;stale=0
        else: stale+=1
        if epoch%20==0: print(f'  seed {seed} GNN epoch {epoch}: validation NLL {vl:.4f}',flush=True)
        if stale>=patience: break
    model.load_state_dict(best_state)
    return model,{'selected_epoch':best_epoch,'elapsed_seconds':time.perf_counter()-start,'history':history}

def fit_mlp(x,y,xv,yv,classes,seed,epochs=250,patience=35):
    seed_all(seed); x=torch.tensor(x,dtype=torch.float32);xv=torch.tensor(xv,dtype=torch.float32)
    y=torch.tensor(y,dtype=torch.long);yv=torch.tensor(yv,dtype=torch.long)
    # Fit scaling only on training data.
    mean=x.mean(0);scale=x.std(0).clamp(min=1.)
    x=(x-mean)/scale;xv=(xv-mean)/scale
    model=MLPBaseline(input_dim=x.shape[1],hidden_dim=32,num_classes=classes)
    opt=torch.optim.Adam(model.parameters(),lr=.01,weight_decay=1e-4)
    best=float('inf');state=None;stale=0;selected=0
    for epoch in range(1,epochs+1):
        model.train();opt.zero_grad();loss=torch.nn.functional.cross_entropy(model(x),y);loss.backward();opt.step()
        model.eval()
        with torch.no_grad(): v=torch.nn.functional.cross_entropy(model(xv),yv).item()
        if v<best-1e-6:best=v;state=copy.deepcopy(model.state_dict());selected=epoch;stale=0
        else:stale+=1
        if stale>=patience:break
    model.load_state_dict(state);model.eval()
    def predict(a):
        with torch.no_grad():return model((torch.tensor(a,dtype=torch.float32)-mean)/scale).softmax(1).numpy()
    return predict,{'selected_epoch':selected,'state_dict':state,'mean':mean,'scale':scale}

def metrics(y,p,classes):
    y=np.asarray(y);p=np.asarray(p);pred=p.argmax(1)
    out={'n':len(y),'accuracy':float(accuracy_score(y,pred)),
         'macro_f1':float(f1_score(y,pred,labels=list(range(classes)),average='macro',zero_division=0)),
         'confusion_matrix':confusion_matrix(y,pred,labels=list(range(classes))).tolist()}
    if classes==2:
        tn,fp,fn,tp=out['confusion_matrix'][0]+out['confusion_matrix'][1]
        out.update(recall=tp/(tp+fn) if tp+fn else None,
                   specificity=tn/(tn+fp) if tn+fp else None,
                   precision=tp/(tp+fp) if tp+fp else 0.,
                   average_precision=float(average_precision_score(y,p[:,1])))
    return out
