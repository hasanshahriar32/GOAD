"""Provenance, split checks, and uncertainty for publication experiments."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[3]
LEGACY = ROOT / 'thesis_research/src/phase2_certgraph'
if str(LEGACY) not in sys.path:
    sys.path.insert(0, str(LEGACY))

def fingerprint(data, target=0):
    """Hash observable model inputs, excluding labels and split metadata."""
    h = hashlib.sha256(str(target).encode())
    for n in sorted(data.node_types):
        a = data[n].x.detach().cpu().contiguous().numpy()
        h.update(str((n, a.shape, str(a.dtype))).encode()); h.update(a.tobytes())
    for e in sorted(data.edge_types):
        a = data[e].edge_index.detach().cpu().contiguous().numpy()
        h.update(str((e, a.shape)).encode()); h.update(a.tobytes())
    return h.hexdigest()

def assert_disjoint(splits):
    seen = {}
    counts = {}
    for name, samples in splits.items():
        hashes = set()
        for d, _, ti in samples:
            h = fingerprint(d, ti)
            if h in seen and seen[h] != name:
                raise ValueError(f'Input overlap between {seen[h]} and {name}: {h}')
            seen[h] = name; hashes.add(h)
        counts[name] = {'samples': len(samples), 'unique_inputs':len(hashes)}
    return counts

def write_json(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)

def environment():
    import torch_geometric, sklearn, scipy
    source = list((ROOT/'thesis_research/src/publication_validation').glob('*.py'))
    source += list(LEGACY.glob('*.py'))
    return {'python':platform.python_version(),'torch':torch.__version__,
            'pyg':torch_geometric.__version__,'sklearn':sklearn.__version__,
            'scipy':scipy.__version__, 'platform':platform.platform(),
            'threads':torch.get_num_threads(),
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source)}}

def bootstrap_interval(values, seed=20261014, repeats=2000):
    """Percentile interval resampling independent experimental units (families)."""
    values=np.asarray(values,dtype=float)
    rng=np.random.default_rng(seed)
    means=np.array([rng.choice(values,len(values),replace=True).mean() for _ in range(repeats)])
    return [float(x) for x in np.quantile(means,[.025,.975])]
