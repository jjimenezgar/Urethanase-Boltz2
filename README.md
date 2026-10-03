# Urethanase-Boltz2

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jjimenezgar/Urethanase-Boltz2/blob/main/notebooks/Urethanase_Boltz2_Colab.ipynb)

A small, reproducible structural-ML benchmark asking whether **Boltz-2** can recover the experimentally observed binding mode of a polyurethane-relevant carbamate substrate in the urethanase **UMG-SP2**.

## Scientific question

Given only the experimental protein construct sequence and ligand identity, how closely does a Boltz-2 co-folded complex reproduce the X-ray complex deposited as **PDB 8XTC**?

This is a portfolio benchmark, not a claim of a new model or a new polyurethane-degradation method.

## Experimental reference

PDB **8XTC** is an X-ray structure (2.40 Å) of UMG-SP2 in complex with the carbamate ligand **A1D5H** (4-hydroxybutyl N-(4-aminophenyl)carbamate). The benchmark uses the exact protein construct represented in 8XTC rather than silently substituting a canonical/WT sequence.

The reference structure is used **only for evaluation**, never as a Boltz template or structural constraint.

## Benchmark

1. Download and validate the 8XTC experimental reference.
2. Extract the experimental protein sequence and create a Boltz-2 YAML input with ligand CCD code `A1D5H`.
3. Run Boltz-2 without a structural template.
4. Compare the predicted complex with the X-ray reference.
5. Report ligand pose RMSD after protein alignment, protein C-alpha RMSD, contact recovery, and catalytic-site geometry.

> **Important limitation:** this is a retrospective benchmark. Model-training overlap with public PDB structures must be considered before interpreting pose recovery as evidence of generalization. The project therefore avoids claims of prospective accuracy.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/fetch_reference.py
python scripts/build_boltz_input.py
pytest
```

On a CUDA machine/Colab, install Boltz separately and run:

```bash
pip install "boltz[cuda]"
boltz predict inputs/umg_sp2_a1d5h.yaml --use_msa_server --out_dir results/boltz2
```

Then evaluate a predicted structure:

```bash
urethanase-boltz2 evaluate \
  --reference data/reference/8XTC.cif \
  --prediction path/to/predicted_model.cif \
  --ligand A1D5H \
  --output results/metrics.json
```

## Scope

The MVP intentionally excludes fine-tuning, MD, web apps, and deployment infrastructure. Boltz-2 inference is the ML component; the contribution of this repository is rigorous experimental setup and evaluation.

## References

- Li et al. (2025), *Advanced Science*, "Structure-Guided Engineering of a Versatile Urethanase Improves Its Polyurethane Depolymerization Activity."
- RCSB PDB: 8XTC.
- Passaro et al. (2025), *Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction*.

## License

MIT.
