"""Semantic and experimental-integrity tests; no neural training required."""
import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/publication_validation'))
import torch
from common import assert_disjoint, fingerprint
from generator import generate_dataset
from esc13_cases import make_family, make_split, reference, independent_reference, to_pyg, MUTATIONS
from model import CertGraph

class PublicationValidationTests(unittest.TestCase):
    def test_namespaced_streams_disjoint(self):
        a=generate_dataset(28,seed=42,namespace='test-train');b=generate_dataset(28,seed=42,namespace='test-test')
        assert_disjoint({'train':a,'test':b})
        self.assertEqual([fingerprint(d,t) for d,_,t in a],[fingerprint(d,t) for d,_,t in generate_dataset(28,seed=42,namespace='test-train')])
        with self.assertRaises(ValueError):assert_disjoint({'a':a,'b':a})
    def test_all_interventions_flip_label(self):
        for seed in [3,7,11]:
            for depth in [0,1,3,7]:
                for mutation in MUTATIONS:
                    pair=make_family('test',seed,1,depth,mutation=mutation)
                    self.assertEqual([reference(c) for c in pair],[1,0])
                    for c in pair:self.assertEqual(reference(c),independent_reference(c))
    def test_reference_agreement_arbitrary_deleted_edges(self):
        # Labels recomputed independently after perturbation, not retained by fiat.
        a,_=make_family('arbitrary',9,2,3)
        for key,edges in a['edges'].items():
            for i in range(len(edges)):
                c=copy.deepcopy(a);c['edges'][key].pop(i)
                self.assertEqual(reference(c),independent_reference(c))
    def test_families_stay_disjoint(self):
        a=make_split('train',1,12);b=make_split('test',1,12)
        self.assertFalse({c['family'] for c in a}&{c['family'] for c in b})
        assert_disjoint({'train':[to_pyg(c) for c in a],'test':[to_pyg(c) for c in b]})
    def test_remote_membership_pair_indistinguishable_to_two_layer_model(self):
        torch.manual_seed(42);torch.set_num_threads(1)
        a,b=make_family('locality',9,1,7,mutation='membership')
        da,ya,ta=to_pyg(a);db,yb,tb=to_pyg(b)
        model=CertGraph(da.metadata(),num_classes=2);model.eval()
        with torch.no_grad():
            pa=model(da.x_dict,da.edge_index_dict)[ta]
            pb=model(db.x_dict,db.edge_index_dict)[tb]
        self.assertNotEqual(ya,yb)
        torch.testing.assert_close(pa,pb,atol=1e-7,rtol=1e-6)

if __name__=='__main__':unittest.main()
