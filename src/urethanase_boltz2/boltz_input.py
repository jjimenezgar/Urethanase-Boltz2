from __future__ import annotations

from pathlib import Path
import yaml


def write_boltz_yaml(sequence: str, ligand_ccd: str, output: Path) -> Path:
    """Write a minimal Boltz complex input without templates."""
    sequence = "".join(sequence.split()).upper()
    if not sequence or any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in sequence):
        raise ValueError("Protein sequence contains unsupported residues")
    doc = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": sequence}},
            {"ligand": {"id": "B", "ccd": ligand_ccd}},
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(doc, sort_keys=False))
    return output
