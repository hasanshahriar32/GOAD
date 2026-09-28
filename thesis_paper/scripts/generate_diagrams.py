"""
Generate publication-quality diagrams for the thesis:
1. figures/adcs_attack_graph_schema.png      (Figure 2.1)
2. figures/esc13_attack_path_diagram.png     (Figure 2.2)
3. figures/certgraph_architecture_diagram.png (Figure 3.1)
4. figures/neuro_symbolic_pipeline.png       (Figure 8.1)
"""
import sys
import os

# Add scripts directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_publication_diagrams import (
    generate_adcs_schema,
    generate_esc13_diagram,
    generate_certgraph_architecture,
    generate_neuro_symbolic_pipeline
)

if __name__ == '__main__':
    generate_adcs_schema()
    generate_esc13_diagram()
    generate_certgraph_architecture()
    generate_neuro_symbolic_pipeline()
    print("All 4 publication diagrams generated successfully.")
