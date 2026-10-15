# Completed benchmark — 14 October 2026

Boltz-2 recovered a similar protein backbone but did not closely reproduce the
experimental ligand pose in this single-sample run. The ligand retained part of
the experimental contact environment despite a substantial atom-coordinate
difference after protein alignment.

| Metric | Result |
|---|---:|
| Protein Cα RMSD | 1.3471 Å |
| Matched Cα atoms | 440 (reference: 440; prediction: 454) |
| Ligand heavy-atom pose RMSD | 7.0901 Å |
| Matched ligand heavy atoms | 16, complete name/element correspondence |
| Contact precision, 4 Å cutoff | 66.67% (10/15) |
| Contact recall, 4 Å cutoff | 66.67% (10/15) |
| Reference ALA190 CB–ligand minimum distance | 3.0636 Å |
| Prediction ALA190 CB–ligand minimum distance | 3.5622 Å |

![Ligand comparison after protein alignment](../results/report/ligand_overlay.png)

Blue points are experimental ligand heavy atoms; orange points are predicted
atoms. Grey lines connect corresponding atom names, rather than chemical bonds.

## Protocol and provenance

The exact 454-position 8XTC construct and CCD ligand A1D5H were used without a
structural template or pocket constraint. The experimental ligand selected was
chain A, residue 504; the predicted ligand was chain B, residue 1. One sample was
produced with seed 42, three recycling steps and 200 diffusion steps. No
prediction selection used reference pose accuracy.

The calculation ran on an NVIDIA A100 80GB PCIe in Hyperion. GPU test job
7685059 took 3 minutes 58 seconds, including first-time data/weight setup and MSA;
the prediction itself took 27 seconds and reported zero failed examples.
Its wrapper then failed because it expected an older output directory layout.
The corrected evaluator used the existing prediction in CPU test job 7685109,
which completed in 7 seconds. No regular job or second inference was needed.
Boltz's ModelCIF canonical sequence consists of X characters; the evaluator
recovers and validates the complete identity from `_entity_poly_seq.mon_id`.

The [manifest](../results/report/manifest.json) preserves the original command,
versions, hashes, original wrapper error and subsequent evaluation command.
The [metrics](../results/report/metrics.json) record atom counts and contacts.
[Resolved environment](../cluster/environment.freeze.txt) records installed versions.
Eight offline tests passed on Hyperion after the evaluator corrections.

## Limits of interpretation

This is a retrospective descriptive result from one sample. It does not establish
prospective generalization, a success rate across seeds, or catalytic activity.
Possible overlap with model training structures is unresolved. No post hoc
pass/fail threshold is used. The input contains one protein chain; the deposited
biological assembly is a dimer. Missing experimental residues are excluded from
Cα alignment. Ligand RMSD uses CCD atom names without a chemical-symmetry
correction. Position 190 in this construct is alanine; its CB distance is a site
marker and cannot replace a catalytic serine hydroxyl geometry measurement.

## Completed ten-seed follow-up

Nine additional seeds (43–51) used the same saved MSA and inference settings.
All three GPU test batches completed with exit code zero: jobs 7693078 and
7693079 each took 5 minutes 42 seconds; job 7693384 took 3 minutes 57 seconds.
No regular job was submitted for this follow-up.

Across all ten seeds, ligand RMSD has a median of 7.046 Å and an interquartile
range of 6.731–7.108 Å. The lowest value is 2.791 Å (seed 43), compared with
7.090 Å for the original seed 42. The other nine values span 6.320–7.213 Å.
This shows that sampling can produce a substantially closer pose, but most of
these samples still differ strongly from experiment. Ten seeds do not establish
a prospective success rate. The maximum confidence score occurs for seed 45,
whose ligand RMSD is 7.114 Å; confidence did not select the lowest-error sample.

The [complete report](../results/multiseed/report.md) includes every seed and
a figure comparing ligand RMSDs, confidence and pairwise pose distances.
All new predictions, metrics, manifests and job logs are saved locally.
