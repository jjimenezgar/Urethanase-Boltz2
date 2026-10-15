# Ten-seed experiment

## Design

The predeclared seeds were 42 (the original sample) and 43–51. All new samples
used the exact stored MSA from seed 42, verified byte-for-byte against the original
CSV. The model settings were Boltz 2.2.1, three recycles, 200 diffusion steps,
one sample per seed, no optional CUDA kernels, and no templates or pocket
constraints. Only the seed changed; a local MSA replaced the original server
request. No samples were discarded based on their experimental pose RMSD.

## Completed Hyperion jobs

| Seeds | Job ID | QOS | Elapsed | Final state |
|---|---|---|---|---|
| 43–45 | 7693078 | test | 00:05:42 | COMPLETED, exit 0 |
| 46–48 | 7693079 | test | 00:05:42 | COMPLETED, exit 0 |
| 49–51 | 7693384 | test | 00:03:57 | COMPLETED, exit 0 |

Each job requested one A100, four CPU cores, 32 GB RAM and a ten-minute limit.
A controller counted all active user `test` jobs every 30 seconds and submitted
the third batch only after a slot became available. It respected a maximum of
two pending/running jobs and did not alter unrelated jobs. Jobs ran from
`/scratch/jcjimenez/Urethanase-Boltz2-benchmark` and reused cached model assets.
Each seed was saved and evaluated independently.

All three jobs finished on 15 October 2026. The nine new predictions, metrics,
confidence files, manifests and job logs have been downloaded and verified.
No regular job was required and no seed jobs remain scheduled by this campaign.
The [controller record](../results/multiseed/controller_status.json) preserves
job IDs and final states; [logs](../results/multiseed/logs/) preserve execution output.

## Results and reproduction

The [complete report](../results/multiseed/report.md) includes all ten seeds.
[The CSV](../results/multiseed/seeds.csv) contains per-seed metrics, while
[summary.json](../results/multiseed/summary.json) stores statistics and the
pairwise ligand RMSD matrix. Distances use the original CCD atom names without
symmetry correction. No post hoc pose-clustering threshold is applied.

```bash
python scripts/verify_benchmark.py
python scripts/summarize_seeds.py
python scripts/compare_poses.py
```

The summary reports all seeds, median, interquartile range and extrema.
Confidence is compared descriptively with observed error. The lowest RMSD is a
retrospective diagnostic, not a prospectively selected prediction; ten samples
from one complex do not establish a general success rate.

## Historical cluster helpers

`cluster/seed_batch.sbatch` records the batch command. The controller and
fetch helper in `scripts/` target this specific completed Hyperion campaign;
they are retained for provenance, not as a portable scheduler for arbitrary
accounts. The controller state is complete. New experiments should use fresh
output directories, job IDs and seed plans. See [cluster notes](../cluster/README.md).
