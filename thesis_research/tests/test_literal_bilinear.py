import unittest
import torch
from thesis_research.src.lineage_constraints.literal_bilinear import LiteralBilinearGNN


class LiteralBilinearTests(unittest.TestCase):
    def inputs(self):
        torch.manual_seed(62003)
        x=torch.randn(2,5,16);a=torch.zeros(2,3,5,5,dtype=torch.bool)
        a[:,0,0,1]=True;a[:,1,1,3]=True;a[:,2,2,3]=True
        return x,a,torch.tensor([[0,1,1,2,3]]*2),torch.ones(2,5,dtype=torch.bool),torch.tensor([3,3])

    def test_node_relabeling_preserves_predictions(self):
        values=self.inputs();model=LiteralBilinearGNN();model.eval();p=torch.tensor([3,0,4,1,2])
        original=model(*values)
        x,a,types,valid,target=values
        changed=model(x[:,p],a[:,:,p][:,:,:,p],types[:,p],valid[:,p],torch.tensor([0,0]))
        self.assertTrue(torch.allclose(original,changed,atol=1e-6))

    def test_bilinear_and_first_step_parameters_receive_gradients(self):
        values=self.inputs();model=LiteralBilinearGNN()
        torch.nn.functional.cross_entropy(model(*values),torch.tensor([0,1])).backward()
        for parameter in (model.encoder,model.layers[0].relation,model.layers[0].bilinear,model.layers[1].bilinear):
            self.assertIsNotNone(parameter.grad)
            self.assertGreater(float(parameter.grad.abs().sum()),0)

    def test_padding_does_not_add_messages(self):
        values=self.inputs();model=LiteralBilinearGNN();model.eval();x,a,types,valid,target=values
        padded_x=torch.nn.functional.pad(x,(0,0,0,2));padded_a=torch.nn.functional.pad(a,(0,2,0,2))
        padded_types=torch.nn.functional.pad(types,(0,2));padded_valid=torch.nn.functional.pad(valid,(0,2),value=False)
        self.assertTrue(torch.allclose(model(*values),model(padded_x,padded_a,padded_types,padded_valid,target),atol=1e-6))
