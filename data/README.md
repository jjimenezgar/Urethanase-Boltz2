# Saved benchmark data

The repository contains the complete lightweight data needed to evaluate all ten
predictions without a GPU or another model download.

| Location | Contents | Approximate total size |
|---|---|---:|
| `reference/8XTC.cif` | Experimental reference, used only for evaluation | 767 KB |
| `predictions/seed_42.cif` … `seed_51.cif` | Ten Boltz-2 complexes, one per seed | 3 MB |
| `msa/umg_sp2_a1d5h_0.csv.gz` | Exact MSA used in the experiment | 2.7 MB |

The reference is from [RCSB PDB 8XTC](https://www.rcsb.org/structure/8XTC).
The original filenames and SHA-256 hashes of each prediction are retained in its
manifest. Renaming a prediction for the repository does not change its bytes.
Seed 42 is recorded in `results/report/`; seeds 43–51 are recorded in
`results/multiseed/seeds/`. Summary tables, compact confidence data, figures and
job logs are also included. The source code and these data occupy about 7 MB;
model weights, CCD caches, PAE/PDE matrices and raw temporary run directories
are excluded from the GitHub update.

## Verify and evaluate

From the repository root:

```bash
sha256sum --check artifacts.sha256
python scripts/verify_benchmark.py
```

The second command also recomputes the ten metric sets and compares them with
the saved values. Install the project first (`pip install -e .`). To evaluate
one structure explicitly:

```bash
urethanase-boltz2 evaluate \
  --reference data/reference/8XTC.cif \
  --prediction data/predictions/seed_43.cif \
  --ligand A1D5H --output results/recomputed_metrics.json
```

## Reuse the saved MSA

```bash
gzip -dc data/msa/umg_sp2_a1d5h_0.csv.gz > data/msa/umg_sp2_a1d5h_0.csv
```

`inputs/umg_sp2_a1d5h_cached_msa.yaml` references that CSV. Use it with
`scripts/run_benchmark.py --input ...` as documented in the main README.
The decompressed CSV is intentionally ignored by Git. A new prediction still
needs Boltz, compatible GPU hardware, model weights and the CCD library.
