"""Generator-matching diagnostic, NOT a complete ADCS exploitability oracle.
These rules were designed after inspecting the legacy generator. Their purpose
is to expose benchmark saturation; real Windows prerequisites are omitted.
"""
from common import LEGACY
from train import extract_graph_counts
from generator import CLASS_TO_IDX

class GeneratorRuleBaseline:
    def predict_one(self, data, target):
        ess,nma,nse,ca,ap,cra,ras,ipo,vacl,_ = data['Template'].x[target].tolist()
        enroll,write,hv,_ = extract_graph_counts(data,target)
        if vacl: return CLASS_TO_IDX['ESC4' if write else 'Safe']
        if ess and ca and nma and not ras: return CLASS_TO_IDX['ESC1' if enroll else 'Safe']
        if ap and nma: return CLASS_TO_IDX['ESC2']
        if (cra or (ras and ca)) and nma: return CLASS_TO_IDX['ESC3']
        if nse and ca: return CLASS_TO_IDX['ESC9']
        if ipo and ca: return CLASS_TO_IDX['ESC13' if enroll and hv else 'Safe']
        return CLASS_TO_IDX['Safe']

    def predict(self, samples):
        return [self.predict_one(d,t) for d,_,t in samples]
