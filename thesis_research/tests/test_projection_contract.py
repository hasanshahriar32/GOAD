import itertools
import unittest
import networkx as nx
from thesis_research.src.lineage_constraints.projection_contract import project


class ProjectionContractTests(unittest.TestCase):
    def test_all_retained_edge_cuts_preserve_every_requested_pair(self):
        g=nx.DiGraph()
        for u,v in [(0,1),(1,2),(0,3),(3,2),(1,3),(4,5)]:g.add_edge(u,v,cost=2,blockable=False,rel="membership")
        pairs=[(0,2),(4,2)];small=project(g,pairs)
        self.assertTrue(all(dict(small[u][v])==dict(g[u][v]) for u,v in small.edges))
        edges=list(g.edges)
        for mask in range(1<<len(edges)):
            cut=[e for i,e in enumerate(edges) if mask>>i&1];full=g.copy();reduced=small.copy()
            full.remove_edges_from(cut);reduced.remove_edges_from(cut)
            for s,t in pairs:self.assertEqual(nx.has_path(full,s,t),nx.has_path(reduced,s,t))

    def test_long_path_is_retained_without_depth_cap(self):
        g=nx.path_graph(12,create_using=nx.DiGraph)
        small=project(g,[(0,11)])
        self.assertEqual(set(small),set(g))
        self.assertTrue(nx.has_path(small,0,11))
