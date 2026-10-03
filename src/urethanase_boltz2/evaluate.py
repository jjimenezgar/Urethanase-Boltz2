from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from Bio.PDB import MMCIFParser, Superimposer


def _structure(path: Path):
    return MMCIFParser(QUIET=True).get_structure(path.stem, str(path))


def _chain(structure, chain_id: str):
    return next(structure.get_models())[chain_id]


def _ca_atoms(structure, chain_id: str):
    return {r.id[1]: r["CA"] for r in _chain(structure, chain_id)
            if r.id[0] == " " and "CA" in r}


def protein_ca_rmsd(reference: Path, prediction: Path, ref_chain="A", pred_chain="A"):
    ref, pred = _structure(reference), _structure(prediction)
    ra, pa = _ca_atoms(ref, ref_chain), _ca_atoms(pred, pred_chain)
    common = sorted(set(ra) & set(pa))
    if len(common) < 3:
        raise ValueError("Fewer than three matched C-alpha atoms")
    sup = Superimposer()
    sup.set_atoms([ra[i] for i in common], [pa[i] for i in common])
    return float(sup.rms), sup, len(common)


def _ligand_residues(structure, residue_name: str):
    hits = [r for r in structure.get_residues() if r.resname.strip() == residue_name]
    if not hits:
        raise ValueError(f"Ligand {residue_name} not found")
    return hits


def _active_site_ligand(structure, residue_name: str, protein_chain: str, catalytic_residue=190):
    """Select the ligand copy closest to catalytic Ser190 OG.

    8XTC contains multiple A1D5H molecules, so selecting the first occurrence
    would make the benchmark dependent on file ordering.
    """
    chain = _chain(structure, protein_chain)
    ser = chain[catalytic_residue]
    anchor = ser["OG"]
    return min(
        _ligand_residues(structure, residue_name),
        key=lambda r: min(np.linalg.norm(a.coord - anchor.coord) for a in r if a.element != "H"),
    )


def _heavy_atoms(residue):
    return {a.name: a for a in residue if a.element != "H"}


def _contacts(chain, ligand, cutoff=4.0):
    ligand_coords = np.asarray([a.coord for a in ligand if a.element != "H"])
    contacts = set()
    for residue in chain:
        if residue.id[0] != " ":
            continue
        for atom in residue:
            if atom.element == "H":
                continue
            if np.any(np.linalg.norm(ligand_coords - atom.coord, axis=1) <= cutoff):
                contacts.add(residue.id[1])
                break
    return contacts


def evaluate_complex(reference: Path, prediction: Path, ligand: str,
                     ref_chain="A", pred_chain="A", catalytic_residue=190):
    protein_rmsd, sup, matched_ca = protein_ca_rmsd(reference, prediction, ref_chain, pred_chain)
    ref, pred = _structure(reference), _structure(prediction)

    ref_res = _active_site_ligand(ref, ligand, ref_chain, catalytic_residue)
    pred_res = _active_site_ligand(pred, ligand, pred_chain, catalytic_residue)
    ref_lig, pred_lig = _heavy_atoms(ref_res), _heavy_atoms(pred_res)
    common = sorted(set(ref_lig) & set(pred_lig))
    if len(common) < 3:
        raise ValueError("Fewer than three matched ligand heavy atoms")

    pred_aligned = {}
    target = []
    coords = []
    for name in common:
        atom = pred_lig[name].copy()
        atom.transform(sup.rotran[0], sup.rotran[1])
        pred_aligned[name] = atom
        coords.append(atom.coord)
        target.append(ref_lig[name].coord)
    ligand_rmsd = float(np.sqrt(np.mean(np.sum((np.asarray(coords)-np.asarray(target))**2, axis=1))))

    ref_contacts = _contacts(_chain(ref, ref_chain), ref_res)
    # Contacts are invariant to rigid alignment.
    pred_contacts = _contacts(_chain(pred, pred_chain), pred_res)
    recovered = ref_contacts & pred_contacts
    precision = len(recovered) / len(pred_contacts) if pred_contacts else 0.0
    recall = len(recovered) / len(ref_contacts) if ref_contacts else 0.0

    ref_ser = _chain(ref, ref_chain)[catalytic_residue]["OG"].coord
    pred_ser = _chain(pred, pred_chain)[catalytic_residue]["OG"].coord
    ref_min = min(float(np.linalg.norm(a.coord-ref_ser)) for a in ref_res if a.element != "H")
    pred_min = min(float(np.linalg.norm(a.coord-pred_ser)) for a in pred_res if a.element != "H")

    return {
        "protein_ca_rmsd_angstrom": protein_rmsd,
        "matched_ca_atoms": matched_ca,
        "ligand_pose_rmsd_angstrom": ligand_rmsd,
        "matched_ligand_heavy_atoms": len(common),
        "contact_cutoff_angstrom": 4.0,
        "reference_contact_residues": sorted(ref_contacts),
        "predicted_contact_residues": sorted(pred_contacts),
        "contact_precision": precision,
        "contact_recall": recall,
        "catalytic_serine_residue": catalytic_residue,
        "reference_ser190_to_ligand_min_distance_angstrom": ref_min,
        "predicted_ser190_to_ligand_min_distance_angstrom": pred_min,
        "reference_chain": ref_chain,
        "prediction_chain": pred_chain,
        "ligand": ligand,
    }


def save_metrics(metrics: dict, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2) + "\n")
