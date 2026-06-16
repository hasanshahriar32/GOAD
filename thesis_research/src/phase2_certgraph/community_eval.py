"""
community_eval.py — Evaluate CertGraph on External Community-Provided BloodHound Datasets
========================================================================================
Loads the trained CertGraph model, parses the external community-provided AD datasets
from the scratch directory, injects ADCS vulnerabilities and hard negatives,
and compares predictions against rule-based baselines.
"""

import os
import json
import torch
import torch.nn.functional as F
from torch_geometric.data import HeteroData

from bloodhound_parser import parse_bloodhound_dir, inject_adcs_vulnerability
from generator import ESC_CLASSES, CLASS_TO_IDX, NUM_CLASSES, template_to_features
from model import CertGraph, RuleBaseline

# Configs matching training
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2

def run_community_eval():
    research_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    checkpoint_path = os.path.join(research_root, "results", "phase2", "certgraph_best.pt")
    scratch_dir = os.path.join(research_root, "scratch", "m4lwhere_data")
    results_dir = os.path.join(research_root, "results", "phase2")
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 75)
    print("EXTERNAL COMMUNITY-PROVIDED DATASET EVALUATION")
    print("=" * 75)

    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}. Train the model first.")

    # List of community domain folders to check
    domain_folders = ["sevenkingdoms_extracted", "essos_extracted", "north_extracted"]
    
    # 2. Instantiate and Load CertGraph Model
    print("[*] Loading trained CertGraph model...")
    checkpoint = torch.load(checkpoint_path, weights_only=False)
    
    # We construct a sample graph from the first folder to trigger lazy init
    sample_dir = os.path.join(scratch_dir, domain_folders[0])
    base_sample_graph = parse_bloodhound_dir(sample_dir)
    sample_graph, _ = inject_adcs_vulnerability(base_sample_graph.clone(), "Safe")
    
    model = CertGraph(
        metadata=sample_graph.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT,
    )
    
    # Lazy initialization trigger
    with torch.no_grad():
        model.eval()
        _ = model(sample_graph.x_dict, sample_graph.edge_index_dict)
        
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print("    Model state dict loaded successfully.")

    rule_baseline = RuleBaseline()

    test_cases = [
        ("ESC1", "ESC1"),
        ("ESC2", "ESC2"),
        ("ESC3", "ESC3"),
        ("ESC4", "ESC4"),
        ("ESC9", "ESC9"),
        ("ESC13", "ESC13"),
        ("Safe", "Safe"),
        ("HN_ESC1", "Safe"),
        ("HN_ESC4", "Safe"),
        ("HN_ESC13", "Safe"),
    ]

    report = {}

    for domain_name in domain_folders:
        domain_dir = os.path.join(scratch_dir, domain_name)
        if not os.path.exists(domain_dir):
            print(f"[!] Warning: directory {domain_dir} does not exist. Skipping.")
            continue
            
        print(f"\n[*] Evaluating domain topology: {domain_name}")
        base_graph = parse_bloodhound_dir(domain_dir)
        print(f"    Loaded: {base_graph['User'].x.shape[0]} Users, {base_graph['Group'].x.shape[0]} Groups, {base_graph['Computer'].x.shape[0]} Computers")
        
        domain_results = []
        
        for case_name, ground_truth in test_cases:
            graph = base_graph.clone()
            
            # Setup templates and CA depending on hard negatives
            if case_name.startswith("HN_"):
                # Inject a hard negative configuration
                from generator import TEMPLATE_GENERATORS
                target_tmpl = TEMPLATE_GENERATORS["Safe"]()
                if case_name == "HN_ESC1":
                    target_tmpl = {
                        "name_flag": 0x1,  # CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
                        "enrollment_flag": 0,
                        "ra_signature": 0,
                        "ekus": ["1.3.6.1.5.5.7.3.2"],
                        "has_issuance_policy_oid": False,
                        "has_vulnerable_acl": False,
                        "schema_version": 2,
                        "hard_negative_type": "ESC1",
                    }
                elif case_name == "HN_ESC4":
                    target_tmpl = {
                        "name_flag": 0,
                        "enrollment_flag": 0,
                        "ra_signature": 0,
                        "ekus": ["1.3.6.1.5.5.7.3.2"],
                        "has_issuance_policy_oid": False,
                        "has_vulnerable_acl": True,
                        "schema_version": 2,
                        "hard_negative_type": "ESC4",
                    }
                elif case_name == "HN_ESC13":
                    target_tmpl = {
                        "name_flag": 0x2000000,
                        "enrollment_flag": 0,
                        "ra_signature": 0,
                        "ekus": ["1.3.6.1.5.5.7.3.2"],
                        "has_issuance_policy_oid": True,
                        "has_vulnerable_acl": False,
                        "schema_version": 2,
                        "hard_negative_type": "ESC13",
                    }
                
                # Ingress CA
                ca_feats = [[1.0, 1.0, 1.0]]
                graph["CA"].x = torch.tensor(ca_feats, dtype=torch.float)
                
                templates = [target_tmpl, TEMPLATE_GENERATORS["Safe"](), TEMPLATE_GENERATORS["Safe"]()]
                template_feats = [template_to_features(t) for t in templates]
                graph["Template"].x = torch.tensor(template_feats, dtype=torch.float)
                graph["Template"].y = torch.tensor([CLASS_TO_IDX["Safe"], CLASS_TO_IDX["Safe"], CLASS_TO_IDX["Safe"]], dtype=torch.long)
                
                # Connect CA
                issued_edges = [[t, 0] for t in range(3)]
                graph["Template", "issued_by", "CA"].edge_index = torch.tensor(issued_edges, dtype=torch.long).t().contiguous()
                
                # Setup edges
                num_users = graph["User"].x.shape[0]
                num_groups = graph["Group"].x.shape[0]
                
                low_priv_users = []
                admin_users = []
                for u_idx in range(num_users):
                    is_admin = graph["User"].x[u_idx, 5].item() > 0.5
                    if is_admin:
                        admin_users.append(u_idx)
                    else:
                        low_priv_users.append(u_idx)
                
                if not low_priv_users:
                    low_priv_users = [0]
                if not admin_users:
                    admin_users = [0]
                
                da_idx = 0
                for g_idx in range(num_groups):
                    name = graph.group_names[g_idx].upper()
                    if "DOMAIN ADMINS" in name or "ADMINISTRATORS" in name:
                        da_idx = g_idx
                        break
                
                enroll_edges = []
                tmpl_acl_edges = []
                policy_edges = []
                
                for t_idx, tmpl in enumerate(templates):
                    is_target = (t_idx == 0)
                    is_hn_esc1 = tmpl.get("hard_negative_type") == "ESC1"
                    is_hn_esc4 = tmpl.get("hard_negative_type") == "ESC4"
                    is_hn_esc13 = tmpl.get("hard_negative_type") == "ESC13"
                    
                    if is_target and is_hn_esc1:
                        # Only admins can enroll
                        for u in admin_users:
                            enroll_edges.append([u, t_idx])
                    elif is_target and is_hn_esc4:
                        # Only admin users can write
                        for u in admin_users:
                            tmpl_acl_edges.append([u, t_idx])
                    elif is_target and is_hn_esc13:
                        # Policy linked to normal group instead of domain admin group
                        policy_edges.append([t_idx, num_groups - 1])
                    else:
                        # Safe template default connections
                        for u in low_priv_users[:2]:
                            enroll_edges.append([u, t_idx])
                        for u in admin_users[:1]:
                            enroll_edges.append([u, t_idx])
                
                if enroll_edges:
                    graph["User", "enrolls", "Template"].edge_index = torch.tensor(enroll_edges, dtype=torch.long).t().contiguous()
                else:
                    graph["User", "enrolls", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)
                    
                if tmpl_acl_edges:
                    graph["User", "write_dacl", "Template"].edge_index = torch.tensor(tmpl_acl_edges, dtype=torch.long).t().contiguous()
                else:
                    graph["User", "write_dacl", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)
                    
                if policy_edges:
                    graph["Template", "linked_to", "Group"].edge_index = torch.tensor(policy_edges, dtype=torch.long).t().contiguous()
                else:
                    graph["Template", "linked_to", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)
                
                target_idx = 0
            else:
                # Normal class injection
                graph, target_idx = inject_adcs_vulnerability(graph, case_name)
            
            # 5. Model Inference
            with torch.no_grad():
                logits = model(graph.x_dict, graph.edge_index_dict)
                pred_idx = logits[target_idx].argmax().item()
                pred_class = ESC_CLASSES[pred_idx]
            
            # Rule Predictor
            feat_vector = graph["Template"].x[target_idx].unsqueeze(0)
            rule_pred_idx = rule_baseline.predict(feat_vector)[0].item()
            rule_pred = ESC_CLASSES[rule_pred_idx]
            
            cg_correct = (pred_class == ground_truth)
            rule_correct = (rule_pred == ground_truth)
            
            domain_results.append({
                "case_name": case_name,
                "ground_truth": ground_truth,
                "certgraph_pred": pred_class,
                "rule_pred": rule_pred,
                "cg_correct": cg_correct,
                "rule_correct": rule_correct
            })
            
            print(f"      - Case: {case_name:<10} | GT: {ground_truth:<5} | CertGraph: {pred_class:<5} ({'✓' if cg_correct else '✗'}) | Heuristics: {rule_pred:<5} ({'✓' if rule_correct else '✗'})")
            
        report[domain_name] = domain_results

    # Save results to JSON
    report_path = os.path.join(results_dir, "community_case_study_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"\n[✓] Community evaluation report saved to: {report_path}")

if __name__ == "__main__":
    run_community_eval()
