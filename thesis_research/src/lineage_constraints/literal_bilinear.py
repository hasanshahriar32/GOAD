"""Literal two-layer, four-head relational attention with bilinear edge gates.

This is a new auditable realization of the manuscript equation, separately from
the historical feature-channel implementation. Encoders, attention, skips and
bilinear gates are trainable with autograd; the baseline uses unit gates.
No closure labels enter forward().
"""
import torch
from torch import nn
from torch.nn import functional as F


class BilinearAttentionLayer(nn.Module):
    def __init__(self,hidden=32,heads=4,relations=3,gated=True):
        super().__init__()
        if hidden%heads:raise ValueError("Hidden width must divide into heads")
        self.heads=heads;self.width=hidden//heads;self.gated=gated
        self.relation=nn.Parameter(torch.empty(relations,heads,hidden,self.width))
        self.attention_source=nn.Parameter(torch.empty(relations,heads,self.width))
        self.attention_target=nn.Parameter(torch.empty(relations,heads,self.width))
        self.bilinear=nn.Parameter(torch.empty(heads,hidden,hidden))
        self.gate_bias=nn.Parameter(torch.zeros(heads))
        self.skip=nn.Linear(hidden,hidden,bias=False)
        nn.init.xavier_uniform_(self.relation)
        nn.init.normal_(self.attention_source,std=.1);nn.init.normal_(self.attention_target,std=.1)
        nn.init.normal_(self.bilinear,std=.02)

    def forward(self,h,adjacency,valid):
        transformed=torch.einsum("bni,rhid->brhnd",h,self.relation)
        source=(transformed*self.attention_source[None,:,:,None,:]).sum(-1)
        target=(transformed*self.attention_target[None,:,:,None,:]).sum(-1)
        scores=F.leaky_relu(target.unsqueeze(-1)+source.unsqueeze(-2),negative_slope=.2)
        edges=adjacency.transpose(-1,-2).unsqueeze(2).bool()
        edges=edges&valid[:,None,None,:,None]&valid[:,None,None,None,:]
        alpha=torch.softmax(scores.masked_fill(~edges,-1e9),dim=-1)*edges
        if self.gated:
            # Source h_s^T W h_t, one scalar bilinear score per head and edge.
            gate=torch.sigmoid(torch.einsum("bsi,hij,btj->bhts",h,self.bilinear,h)+self.gate_bias[None,:,None,None])
            alpha=alpha*gate[:,None]
        messages=torch.einsum("brhts,brhsd->bhtd",alpha,transformed)
        aggregate=messages.permute(0,2,1,3).reshape(h.shape)
        skip=self.skip(h).reshape(h.shape[0],h.shape[1],self.heads,self.width)
        if self.gated:skip=skip*gate.diagonal(dim1=-2,dim2=-1).permute(0,2,1).unsqueeze(-1)
        result=F.elu(aggregate)+skip.reshape(h.shape)
        return result*valid.unsqueeze(-1)


class LiteralBilinearGNN(nn.Module):
    def __init__(self,gated=True,input_dim=16,hidden=32,heads=4,node_types=5,relations=3):
        super().__init__()
        self.encoder=nn.Parameter(torch.empty(node_types,input_dim,hidden))
        self.encoder_bias=nn.Parameter(torch.zeros(node_types,hidden))
        nn.init.xavier_uniform_(self.encoder)
        self.layers=nn.ModuleList([BilinearAttentionLayer(hidden,heads,relations,gated) for _ in range(2)])
        self.readout=nn.Linear(hidden,2)

    def forward(self,x,adjacency,node_types,valid,target):
        h=F.relu(torch.einsum("bni,bnij->bnj",x,self.encoder[node_types])+self.encoder_bias[node_types])
        h=h*valid.unsqueeze(-1)
        for layer in self.layers:h=layer(h,adjacency,valid)
        return self.readout(h[torch.arange(h.shape[0],device=h.device),target])
