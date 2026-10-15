"""Verify published file hashes and recompute all ten saved metric sets on a CPU."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path

from urethanase_boltz2.evaluate import evaluate_complex

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--hashes-only', action='store_true')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
os.chdir(root)
count = 0
for line in Path('artifacts.sha256').read_text().splitlines():
    expected, name = line.split('  ', 1)
    path = (root/name).resolve()
    if root not in path.parents or not path.is_file():
        raise ValueError(f'Missing or invalid artifact: {name}')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Artifact checksum mismatch: {name}')
    count += 1
print(f'Verified {count} published artifact checksums.', flush=True)
if not a.hashes_only:
    plan = json.loads(Path('results/multiseed/plan.json').read_text())
    seeds = [plan['baseline_seed'], *plan['additional_seeds']]
    if len(seeds) != 10 or len(set(seeds)) != 10:
        raise ValueError('Expected ten distinct predeclared seeds')
    for seed in seeds:
        folder = Path('results/report') if seed == plan['baseline_seed'] else Path(f'results/multiseed/seeds/seed_{seed}')
        manifest = json.loads((folder/'manifest.json').read_text())
        if manifest['seed'] != seed or manifest['status'] != 'complete':
            raise ValueError(f'Incomplete or inconsistent manifest for seed {seed}')
        prediction = Path(manifest['prediction'])
        if hashlib.sha256(prediction.read_bytes()).hexdigest() != manifest['prediction_sha256']:
            raise ValueError(f'Prediction hash mismatch for seed {seed}')
        actual = evaluate_complex(Path('data/reference/8XTC.cif'), prediction, 'A1D5H')
        expected = json.loads((folder/'metrics.json').read_text())
        if set(actual) != set(expected):
            raise ValueError(f'Metric fields differ for seed {seed}')
        for key, value in actual.items():
            matches = (math.isclose(value, expected[key], rel_tol=0, abs_tol=1e-6)
                       if isinstance(value, float) else value == expected[key])
            if not matches:
                raise ValueError(f'Metric mismatch: seed {seed}, {key}')
        print(f'Seed {seed}: recomputed metrics match.', flush=True)
