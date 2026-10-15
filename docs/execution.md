# Execution and validation

The 8XTC polymer entity has 454 positions. Position 190 is **ALA**, as verified
from both the deposited sequence and coordinates. The original Ser190 OG
calculation therefore could not run. We now measure distance to ALA190 CB as a
site-position marker; this is not a nucleophilic hydroxyl distance and cannot
establish catalytic competence. We do not infer a named mutation from the entry's
ambiguous mutation metadata.

Protein atoms and contacts use mmCIF `label_seq_id` positions, not author numbers.
The deposited complete polymer sequences must agree. Ligand heavy-atom names
and elements must match completely; partial-atom RMSD is rejected. The reported
RMSD uses CCD atom names and is not corrected for chemical symmetry.

The reference ligand is selected nearest the declared position-190 marker.
Each seed produces one prediction sample; all ten seeds are evaluated without
selection by experimental pose RMSD.
This is a descriptive retrospective benchmark, with possible training overlap.

## Hyperion

Work directory: `/scratch/jcjimenez/Urethanase-Boltz2-benchmark`.
The home directory could not hold a new environment because its quota was exhausted.
Existing files and environments were not removed.

`cluster/test.sbatch` requests one A100 on partition `general`, QOS `test`,
for ten minutes. `cluster/regular.sbatch` uses `gpu-regular`, the GPU variant
of regular service, for four hours. Submit the regular job only if the test
cannot finish inference. Environment setup is separate from the timed test.

```bash
sbatch cluster/test.sbatch
# If needed after checking the test log:
sbatch cluster/regular.sbatch
```

Boltz is pinned to 2.2.1. Each run writes a manifest containing the actual
installed versions, command, seed, timestamps, job ID, and file hashes.
The reference is used only by the evaluator. Keep manifests and metrics with
published results; model weights and caches remain excluded.

## Validation

```bash
PYTHONPATH=src python -m pytest -m 'not integration' -q
```

Offline tests cover identity, rigid transforms, author renumbering, incomplete
ligand atom sets, differing constructs, and a displaced ligand with known RMSD. The real reference self-comparison
is saved in `results/validation/reference_self.json`: it is a validation control,
**not a Boltz prediction**. The completed ten-seed benchmark includes predictions, metrics and interpretation.

For a fresh inference environment, install
`cluster/requirements-inference.txt`; PyTorch is fixed to 2.5.1 and RDKit to
2024.9.6, with NumPy 1.26.4. Optional CUDA acceleration kernels are omitted. The exact resolved
environment is captured in each run's manifest.

The completed Hyperion result is described in [results](results.md). Boltz 2.2.1
creates a `boltz_results_*` subdirectory; the runner locates the unique model_0
CIF recursively. If inference has completed but evaluation needs repair, use:

```bash
python scripts/run_benchmark.py --out-dir results/<existing-run> --evaluate-only
```

This preserves original inference provenance and does not rerun the model.
The evaluator reconstructs all-X ModelCIF canonical sequences from the complete
polymer monomer table, checking known positions for consistency.
