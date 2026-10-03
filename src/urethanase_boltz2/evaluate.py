from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from Bio.PDB import MMCIFParser, Superimposer


def _structure(path: Path):
    return MMCIFParser(QUIET=True).get_structure(path.stem, str(path))


def _ca_atoms(structure, chain_id: str):
    chain = next(structure.get_models())[chain_id]
    return {r.id[1]: r["CA"] for r in chain if r.id[0] == " " and "CA" in r}


def protein_ca_rmsd(reference: Path, prediction: Path, ref_chain="A", pred_chain="A") -> tuple[float, object]:
    ref, pred = _structure(reference), _structure(prediction)
    ra, pa = _ca_atoms(ref, ref_chain), _ca_atoms(pred, pred_chain)
    common = sorted(set(ra) & set(pa))
    if len(common) < 3:
        raise ValueError("Fewer than three matched C-alpha atoms")
    sup = Superimposer()
    sup.set_atoms([ra[i] for i in common], [pa[i] for i in common])
    return float(sup.rms), sup


def ligand_atoms(structure, residue_name: str):
    hits = []
    for residue in structure.get_residues():
        if residue.resname.strip() == residue_name:
            hits.append(residue)
    if not hits:
        raise ValueError(f"Ligand {residue_name} not found")
    # 8XTC contains multiple copies; benchmark the first unless an instance is specified later.
    return {a.name: a for a in hits[0] if a.element != "H"}


def evaluate_complex(reference: Path, prediction: Path, ligand: str, ref_chain="A", pred_chain="A"):
    protein_rmsd, sup = protein_ca_rmsd(reference, prediction, ref_chain, pred_chain)
    ref = _structure(reference)
    pred = _structure(prediction)
    ref_lig = ligand_atoms(ref, ligand)
    pred_lig = ligand_atoms(pred, ligand)
    common = sorted(set(ref_lig) & set(pred_lig))
    if len(common) < 3:
        raise ValueError("Fewer than three matched ligand heavy atoms")
    # Apply the protein-derived superposition to the predicted ligand.
    coords = []
    target = []
    for name in common:
        atom = pred_lig[name].copy()
        atom.transform(sup.rotran[0], sup.rotran[1])
        coords.append(atom.coord)
        target.append(ref_lig[name].coord)
    ligand_rmsd = float(np.sqrt(np.mean(np.sum((np.asarray(coords)-np.asarray(target))**2, axis=1))))
    return {
        "protein_ca_rmsd_angstrom": protein_rmsd,
        "ligand_pose_rmsd_angstrom": ligand_rmsd,
        "matched_ligand_heavy_atoms": len(common),
        "reference_chain": ref_chain,
        "prediction_chain": pred_chain,
        "ligand": ligand,
    }


def save_metrics(metrics: dict, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2) + "\n")
