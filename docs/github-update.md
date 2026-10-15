# Prepared GitHub update

The update contains the completed ten-seed benchmark, all ten compact predicted
complexes, the reference and compressed MSA, corrected evaluation code, offline
tests, CPU reproduction commands, figures, provenance, a revised README and CI
verification. No model weights, scratch caches or duplicate raw runs are included.
Local duplicate outputs have been preserved under ignored `archive/local-runs/`.

The working folder supplied to this session has no usable Git metadata. The
update was therefore also assembled in a separate clone of
`https://github.com/jjimenezgar/Urethanase-Boltz2`, based on commit `5d432b4`.
The completed update was published to `main` on 15 October 2026 in
[commit 64ebb0c](https://github.com/jjimenezgar/Urethanase-Boltz2/commit/64ebb0c329dd77a77d3178157568edfddbac62d5).
The instructions below preserve the preparation workflow for the local ZIP.

## Apply in a normal Git checkout

`dist/urethanase-boltz2-github-update.zip` contains the complete curated project,
with repository-relative paths and no `.git` directory. Extract it into a fresh
checkout of the existing repository, on a new branch. Review the resulting diff.
For example:

```bash
git clone https://github.com/jjimenezgar/Urethanase-Boltz2.git urethanase-update
cd urethanase-update
git switch -c benchmark-ten-seeds
unzip /absolute/path/to/urethanase-boltz2-github-update.zip -d .

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,report]"
pytest -m "not integration"
python scripts/verify_benchmark.py
git diff --check
git status --short
```

Once reviewed, commit the update and push the branch through your usual workflow.
The ZIP contains all tracked project content, so use a fresh checkout to avoid
overwriting unrelated local edits. It deliberately excludes the local archive,
raw run directories and distribution files themselves.

## Suggested commit or pull-request title

Complete ten-seed Boltz-2 urethanase pose benchmark

## Suggested description

Complete a retrospective pose-recovery benchmark on the exact 8XTC construct
and A1D5H ligand. Across ten predeclared seeds, protein Cα RMSD is 0.854–1.347 Å,
while ligand RMSD has a median of 7.046 Å and range of 2.791–7.213 Å. The update
reports every sample and compares original and closest sampled poses.

Correct residue mapping, ModelCIF sequence interpretation and the ALA190 marker;
reject incomplete ligand atom mappings. Include lightweight structures, the
fixed MSA, metrics, run provenance, figures and CPU verification. CI runs offline
tests and recomputes the ten saved metric sets. Training overlap, monomer versus
dimer context and lack of symmetry correction are documented limitations.
