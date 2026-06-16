"""
certgraph_model.py — CertGraph: Certificate-Aware Heterogeneous GNN
=====================================================================
Multi-class ESC vulnerability classifier using heterogeneous graph
attention with relation-specific message passing.

Architecture:
    Node features → HeteroConv(GATConv) Layer 1 (4 heads)
    + Node-specific ResNet skip connection (Layer 1)
    → ReLU + Dropout
    → HeteroConv(GATConv) Layer 2 (1 head)
    + Node-specific ResNet skip connection (Layer 2)
    → Template node embeddings → MLP classifier → ESC class logits

Also includes baseline models for comparison:
    - MLPBaseline: MLP on flat template features only
    - GCNBaseline: Homogeneous GCN (ignores node/edge types)
    - RuleBaseline: Certipy-style heuristic classifier
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, HeteroConv
import numpy as np
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from generator import CLASS_TO_IDX, NUM_CLASSES, TEMPLATE_FEATURE_DIM


# ─────────────────────────────────────────────────────────────────────
# CertGraph — Main Model
# ─────────────────────────────────────────────────────────────────────

class CertGraph(nn.Module):
    """
    Certificate-Aware Heterogeneous Graph Attention Network with Residual Skip Connections.

    Performs multi-class node classification on Template nodes to predict
    their ESC vulnerability class (ESC1/ESC2/ESC3/ESC4/ESC9/ESC13/Safe).
    """

    def __init__(
        self,
        metadata: tuple,
        hidden_channels: int = 32,
        out_channels: int = 16,
        num_classes: int = 7,
        num_heads: int = 4,
        dropout: float = 0.2,
        skip_connections: bool = True,
    ):
        super().__init__()
        self.dropout = dropout
        self.num_classes = num_classes
        self.node_types = metadata[0]
        self._hidden_total = hidden_channels * num_heads
        self._out_channels = out_channels
        self.skip_connections = skip_connections

        # Layer 1: Multi-head GAT per relation type
        self.conv1 = HeteroConv(
            {
                edge_type: GATConv(
                    (-1, -1), hidden_channels, heads=num_heads,
                    add_self_loops=False, dropout=dropout,
                )
                for edge_type in metadata[1]
            },
            aggr="sum",
        )

        # Layer 2: Single-head GAT
        self.conv2 = HeteroConv(
            {
                edge_type: GATConv(
                    hidden_channels * num_heads, out_channels, heads=1,
                    concat=False, add_self_loops=False, dropout=dropout,
                )
                for edge_type in metadata[1]
            },
            aggr="sum",
        )

        # Lazy skip connection layers — will be initialized on first forward pass
        self._projections_initialized = False
        self.skip1 = nn.ModuleDict()
        self.skip2 = nn.ModuleDict()

        # Classification head for Template nodes
        self.classifier = nn.Sequential(
            nn.Linear(out_channels, out_channels),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(out_channels, num_classes),
        )

    def _ensure_projections(self, x_dict: dict[str, torch.Tensor]):
        """Create skip connection projection layers on first pass."""
        if self._projections_initialized:
            return
        for ntype, x in x_dict.items():
            self.skip1[ntype] = nn.Linear(x.shape[1], self._hidden_total)
            self.skip2[ntype] = nn.Linear(self._hidden_total, self._out_channels)
        self._projections_initialized = True

    def forward(
        self,
        x_dict: dict[str, torch.Tensor],
        edge_index_dict: dict[tuple, torch.Tensor],
    ) -> torch.Tensor:
        """
        Forward pass. Returns logits for Template nodes.

        Returns:
            Tensor of shape [num_templates, num_classes]
        """
        self._ensure_projections(x_dict)

        # Message passing layer 1
        x_dict_1 = self.conv1(x_dict, edge_index_dict)
        
        # Apply Layer 1 skip connections (ResNet residual block)
        out_dict_1 = {}
        for k, v in x_dict.items():
            proj_val = self.skip1[k](v)
            if k in x_dict_1 and x_dict_1[k] is not None:
                if self.skip_connections:
                    out_dict_1[k] = x_dict_1[k] + proj_val
                else:
                    out_dict_1[k] = x_dict_1[k]
            else:
                out_dict_1[k] = proj_val
                
        out_dict_1 = {k: F.relu(v) for k, v in out_dict_1.items()}
        out_dict_1 = {
            k: F.dropout(v, p=self.dropout, training=self.training)
            for k, v in out_dict_1.items()
        }

        # Message passing layer 2
        x_dict_2 = self.conv2(out_dict_1, edge_index_dict)
        
        # Apply Layer 2 skip connections
        out_dict_2 = {}
        for k, v in out_dict_1.items():
            proj_val = self.skip2[k](v)
            if k in x_dict_2 and x_dict_2[k] is not None:
                if self.skip_connections:
                    out_dict_2[k] = x_dict_2[k] + proj_val
                else:
                    out_dict_2[k] = x_dict_2[k]
            else:
                out_dict_2[k] = proj_val

        # Classify Template nodes
        template_emb = out_dict_2["Template"]
        logits = self.classifier(template_emb)
        return logits

    def get_embeddings(
        self,
        x_dict: dict[str, torch.Tensor],
        edge_index_dict: dict[tuple, torch.Tensor],
    ) -> dict[str, torch.Tensor]:
        """Get node embeddings from layer 2 (before classifier)."""
        self._ensure_projections(x_dict)
        
        x_dict_1 = self.conv1(x_dict, edge_index_dict)
        out_dict_1 = {}
        for k, v in x_dict.items():
            proj_val = self.skip1[k](v)
            if k in x_dict_1 and x_dict_1[k] is not None:
                if self.skip_connections:
                    out_dict_1[k] = x_dict_1[k] + proj_val
                else:
                    out_dict_1[k] = x_dict_1[k]
            else:
                out_dict_1[k] = proj_val
        out_dict_1 = {k: F.relu(v) for k, v in out_dict_1.items()}
        
        x_dict_2 = self.conv2(out_dict_1, edge_index_dict)
        out_dict_2 = {}
        for k, v in out_dict_1.items():
            proj_val = self.skip2[k](v)
            if k in x_dict_2 and x_dict_2[k] is not None:
                if self.skip_connections:
                    out_dict_2[k] = x_dict_2[k] + proj_val
                else:
                    out_dict_2[k] = x_dict_2[k]
            else:
                out_dict_2[k] = proj_val
                
        return out_dict_2

    def get_attention_weights(
        self,
        x_dict: dict[str, torch.Tensor],
        edge_index_dict: dict[tuple, torch.Tensor],
    ) -> dict[tuple, tuple[torch.Tensor, torch.Tensor]]:
        """Extract attention weights for conv1."""
        self._ensure_projections(x_dict)
        attentions = {}
        for edge_type, edge_index in edge_index_dict.items():
            src, rel, dst = edge_type
            h_src = x_dict[src]
            h_dst = x_dict[dst]
            conv = self.conv1.convs[edge_type]
            _, (edge_index_out, alpha) = conv((h_src, h_dst), edge_index, return_attention_weights=True)
            attentions[edge_type] = (edge_index_out, alpha)
        return attentions


# ─────────────────────────────────────────────────────────────────────
# Baseline 1: MLP on flat template features
# ─────────────────────────────────────────────────────────────────────

class MLPBaseline(nn.Module):
    """MLP classifier using only template features (no graph structure)."""

    def __init__(self, input_dim: int = 10, hidden_dim: int = 32, num_classes: int = 7):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ─────────────────────────────────────────────────────────────────────
# Baseline 2: Rule-based (Certipy-style heuristic)
# ─────────────────────────────────────────────────────────────────────

class RuleBaseline:
    """
    Deterministic rule-based classifier mimicking Certipy/Certify logic.
    Uses the 10-dim template feature vector directly.

    Feature indices:
        0: enrollee_supplies_subject
        1: no_manager_approval
        2: no_security_extension
        3: has_client_auth
        4: has_any_purpose
        5: has_cert_req_agent
        6: ra_signature_required
        7: has_issuance_policy_oid
        8: has_vulnerable_acl
        9: schema_version_norm
    """

    def predict(self, features: torch.Tensor) -> torch.Tensor:
        """
        Classify templates based on deterministic rules.

        Args:
            features: [num_templates, 10] feature tensor

        Returns:
            [num_templates] predicted class indices
        """
        preds = []
        for i in range(features.shape[0]):
            f = features[i]
            ess = f[0].item()     # enrollee_supplies_subject
            nma = f[1].item()     # no_manager_approval
            nse = f[2].item()     # no_security_extension
            ca = f[3].item()      # has_client_auth
            ap = f[4].item()      # has_any_purpose
            cra = f[5].item()     # has_cert_req_agent
            ras = f[6].item()     # ra_signature_required
            ipo = f[7].item()     # has_issuance_policy_oid
            vacl = f[8].item()    # has_vulnerable_acl

            # Priority ordering matters
            if ess > 0 and ca > 0 and nma > 0 and ras < 0.5:
                preds.append(0)  # ESC1
            elif ap > 0 and nma > 0:
                preds.append(1)  # ESC2
            elif (cra > 0 or ras > 0) and nma > 0:
                preds.append(2)  # ESC3
            elif vacl > 0:
                preds.append(3)  # ESC4
            elif nse > 0 and ca > 0:
                preds.append(4)  # ESC9
            elif ipo > 0 and ca > 0:
                preds.append(5)  # ESC13
            else:
                preds.append(6)  # Safe

        return torch.tensor(preds, dtype=torch.long)


if __name__ == "__main__":
    print("CertGraph model with skip connections initialized.")
