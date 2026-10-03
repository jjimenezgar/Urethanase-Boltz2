# Benchmark protocol

## Question

Can Boltz-2 recover the experimentally observed active-site binding mode of the short-chain carbamate A1D5H in the UMG-SP2 construct deposited as PDB 8XTC?

## Reference

8XTC is an X-ray structure at 2.40 Å. It contains two protein chains and multiple copies of A1D5H. The evaluator selects the ligand copy closest to catalytic Ser190 rather than relying on mmCIF record order.

The exact polymer entity sequence from 8XTC is extracted automatically and used as the Boltz protein sequence. This matters because the PDB entry is labelled `umgsp2-mut` and is not assumed to be interchangeable with the 462-residue UMG-SP2 construct in 8WDW.

## Leakage control

8XTC coordinates are never passed to Boltz as a template, pocket constraint, or contact constraint. Only the sequence and ligand CCD identity are supplied.

This does **not** establish that 8XTC was absent from Boltz-2 training data. Therefore this is explicitly a retrospective structure-recovery benchmark, not a prospective generalization test.

## Primary metrics

- ligand heavy-atom pose RMSD after C-alpha alignment of the protein;
- protein C-alpha RMSD;
- 4 Å protein-ligand contact precision and recall;
- minimum distance between catalytic Ser190 OG and the ligand.

Metrics are descriptive. No arbitrary pass/fail threshold is introduced after seeing the prediction.

## Reproducibility

The repository records the input-generation code, Boltz input, model command, experimental PDB identifier and evaluation code. Generated model weights, MSA caches and predictions are not committed.
