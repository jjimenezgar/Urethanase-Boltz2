from __future__ import annotations

import json
from pathlib import Path
import numpy as np
from Bio.PDB import MMCIFParser, Superimposer
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from .structure import polymer_sequences


def _structure(path: Path):
    structure = MMCIFParser(QUIET=True).get_structure(path.stem, str(path))
    # Use polymer sequence positions rather than author residue numbers.
    d = MMCIF2Dict(str(path))
    positions = {}
    entities = {}
    for chain, number, insertion, position, entity in zip(
        d["_atom_site.auth_asym_id"], d["_atom_site.auth_seq_id"],
        d["_atom_site.pdbx_PDB_ins_code"], d["_atom_site.label_seq_id"],
        d["_atom_site.label_entity_id"],
    ):
        if position not in (".", "?"):
            positions[(chain, int(number), " " if insertion in (".", "?") else insertion)] = int(position)
            entities[chain] = entity
    sequences = polymer_sequences(d)
    for chain in next(structure.get_models()):
        if chain.id in entities:
            chain.xtra["sequence"] = "".join(sequences[entities[chain.id]].split())
        for residue in chain:
            key = (chain.id, residue.id[1], residue.id[2])
            if residue.id[0] == " " and key in positions:
                residue.xtra["sequence_position"] = positions[key]
    return structure


def _chain(structure, chain_id: str):
    return next(structure.get_models())[chain_id]


def _ca_atoms(structure, chain_id: str):
    return {r.xtra["sequence_position"]: r["CA"] for r in _chain(structure, chain_id)
            if r.id[0] == " " and "CA" in r}


def protein_ca_rmsd(reference: Path, prediction: Path, ref_chain="A", pred_chain="A"):
    ref, pred = _structure(reference), _structure(prediction)
    if _chain(ref, ref_chain).xtra["sequence"] != _chain(pred, pred_chain).xtra["sequence"]:
        raise ValueError("Protein construct sequences differ; explicit sequence mapping is required")
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


def _site_anchor(structure, protein_chain, catalytic_residue=190):
    chain = _chain(structure, protein_chain)
    residue = next((r for r in chain if r.xtra.get("sequence_position") == catalytic_residue), None)
    if residue is None:
        raise ValueError(f"Site residue {catalytic_residue} is unresolved")
    # 8XTC has ALA190, not SER190. CB is a positional marker, not a hydroxyl.
    atom_name = {"ALA": "CB", "SER": "OG"}.get(residue.resname)
    if atom_name is None or atom_name not in residue:
        raise ValueError("Site anchor requires resolved ALA CB or SER OG")
    return residue[atom_name]


def _active_site_ligand(structure, residue_name: str, protein_chain: str, catalytic_residue=190):
    """Select the ligand nearest the predeclared position-190 site marker."""
    anchor = _site_anchor(structure, protein_chain, catalytic_residue)
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
                contacts.add(residue.xtra["sequence_position"])
                break
    return contacts


def evaluate_complex(reference: Path, prediction: Path, ligand: str,
                     ref_chain="A", pred_chain="A", catalytic_residue=190):
    protein_rmsd, sup, matched_ca = protein_ca_rmsd(reference, prediction, ref_chain, pred_chain)
    ref, pred = _structure(reference), _structure(prediction)

    ref_res = _active_site_ligand(ref, ligand, ref_chain, catalytic_residue)
    pred_res = _active_site_ligand(pred, ligand, pred_chain, catalytic_residue)
    ref_lig, pred_lig = _heavy_atoms(ref_res), _heavy_atoms(pred_res)
    if set(ref_lig) != set(pred_lig):
        raise ValueError("Ligand heavy-atom names differ; complete atom mapping is required")
    common = sorted(ref_lig)
    if any(ref_lig[n].element != pred_lig[n].element for n in common):
        raise ValueError("Ligand atom elements differ")
    if len(common) < 3:
        raise ValueError("Fewer than three matched ligand heavy atoms")

    target = []
    coords = []
    for name in common:
        atom = pred_lig[name].copy()
        atom.transform(sup.rotran[0], sup.rotran[1])
        coords.append(atom.coord)
        target.append(ref_lig[name].coord)
    ligand_rmsd = float(np.sqrt(np.mean(np.sum((np.asarray(coords)-np.asarray(target))**2, axis=1))))

    ref_contacts = _contacts(_chain(ref, ref_chain), ref_res)
    # Contacts are invariant to rigid alignment.
    pred_contacts = _contacts(_chain(pred, pred_chain), pred_res)
    recovered = ref_contacts & pred_contacts
    precision = len(recovered) / len(pred_contacts) if pred_contacts else 0.0
    recall = len(recovered) / len(ref_contacts) if ref_contacts else 0.0

    ref_ser = _site_anchor(ref, ref_chain, catalytic_residue).coord
    pred_ser = _site_anchor(pred, pred_chain, catalytic_residue).coord
    ref_min = min(float(np.linalg.norm(a.coord-ref_ser)) for a in ref_res if a.element != "H")
    pred_min = min(float(np.linalg.norm(a.coord-pred_ser)) for a in pred_res if a.element != "H")

    return {
        "protein_ca_rmsd_angstrom": protein_rmsd,
        "matched_ca_atoms": matched_ca,
        "reference_ca_atoms": len(_ca_atoms(ref, ref_chain)),
        "prediction_ca_atoms": len(_ca_atoms(pred, pred_chain)),
        "reference_ligand_chain": ref_res.parent.id,
        "reference_ligand_residue_number": ref_res.id[1],
        "prediction_ligand_chain": pred_res.parent.id,
        "prediction_ligand_residue_number": pred_res.id[1],
        "ligand_atom_mapping": "complete CCD atom names; no symmetry correction",
        "ligand_pose_rmsd_angstrom": ligand_rmsd,
        "matched_ligand_heavy_atoms": len(common),
        "contact_cutoff_angstrom": 4.0,
        "reference_contact_residues": sorted(ref_contacts),
        "predicted_contact_residues": sorted(pred_contacts),
        "contact_precision": precision,
        "contact_recall": recall,
        "site_sequence_position": catalytic_residue,
        "reference_site_residue": _site_anchor(ref, ref_chain, catalytic_residue).parent.resname,
        "reference_site_atom": _site_anchor(ref, ref_chain, catalytic_residue).name,
        "prediction_site_atom": _site_anchor(pred, pred_chain, catalytic_residue).name,
        "reference_site_anchor_to_ligand_min_distance_angstrom": ref_min,
        "predicted_site_anchor_to_ligand_min_distance_angstrom": pred_min,
        "reference_chain": ref_chain,
        "prediction_chain": pred_chain,
        "ligand": ligand,
    }


def save_metrics(metrics: dict, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2) + "\n")
