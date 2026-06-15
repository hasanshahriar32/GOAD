"""
model.py — Heterogeneous Graph Attention Network for AD Attack Path Detection
==============================================================================
Two-layer HGAT using PyTorch Geometric's HeteroConv with relation-specific
GATConv layers. Includes a LinkPredictor decoder for edge existence scoring.

Architecture:
    Input → Linear projection (per type) → GATConv Layer 1 (4 heads)
         → ReLU + Dropout → GATConv Layer 2 (1 head) → Node embeddings
    
    LinkPredictor: dot-product decoder on source/target embeddings
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, HeteroConv, Linear


class HGAT(nn.Module):
    """
    Heterogeneous Graph Attention Network.

    Uses HeteroConv to wrap relation-specific GATConv layers. Each edge type
    gets its own GAT convolution, and messages are aggregated per-node via
    summation across relation types.

    Args:
        metadata: Tuple of (node_types, edge_types) from HeteroData.metadata()
        hidden_channels: Hidden dimension after first GAT layer
        out_channels: Output embedding dimension
        num_heads: Number of attention heads in the first layer
        dropout: Dropout probability
    """

    def __init__(
        self,
        metadata: tuple,
        hidden_channels: int = 32,
        out_channels: int = 16,
        num_heads: int = 4,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.dropout = dropout

        # Layer 1: Multi-head GAT per relation
        # (-1, -1) enables lazy initialization for heterogeneous input dims
        self.conv1 = HeteroConv(
            {
                edge_type: GATConv(
                    (-1, -1),
                    hidden_channels,
                    heads=num_heads,
                    add_self_loops=False,
                    dropout=dropout,
                )
                for edge_type in metadata[1]
            },
            aggr="sum",
        )

        # Layer 2: Single-head GAT to produce final embeddings
        self.conv2 = HeteroConv(
            {
                edge_type: GATConv(
                    hidden_channels * num_heads,
                    out_channels,
                    heads=1,
                    concat=False,
                    add_self_loops=False,
                    dropout=dropout,
                )
                for edge_type in metadata[1]
            },
            aggr="sum",
        )

    def forward(
        self,
        x_dict: dict[str, torch.Tensor],
        edge_index_dict: dict[tuple, torch.Tensor],
    ) -> dict[str, torch.Tensor]:
        """
        Forward pass through two GAT layers.

        Args:
            x_dict: Dict mapping node type → feature tensor
            edge_index_dict: Dict mapping edge type → edge_index tensor

        Returns:
            Dict mapping node type → embedding tensor (out_channels dim)
        """
        # Layer 1: multi-head attention + ReLU
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        x_dict = {
            key: F.dropout(x, p=self.dropout, training=self.training)
            for key, x in x_dict.items()
        }

        # Layer 2: single-head attention → final embeddings
        x_dict = self.conv2(x_dict, edge_index_dict)

        return x_dict


class LinkPredictor(nn.Module):
    """
    Dot-product link predictor for edge existence scoring.

    Given source and target node embeddings and an edge_index, computes
    the dot product between corresponding source-target pairs as a
    scalar score (logit) for each edge.
    """

    def forward(
        self,
        src_embeddings: torch.Tensor,
        dst_embeddings: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            src_embeddings: [num_src_nodes, dim] source node embeddings
            dst_embeddings: [num_dst_nodes, dim] target node embeddings
            edge_index: [2, num_edges] source/target index pairs

        Returns:
            [num_edges] scalar logits for each edge
        """
        src = src_embeddings[edge_index[0]]
        dst = dst_embeddings[edge_index[1]]
        return (src * dst).sum(dim=-1)
