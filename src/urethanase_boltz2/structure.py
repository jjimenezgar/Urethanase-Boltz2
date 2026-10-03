from __future__ import annotations

from pathlib import Path
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

def _as_list(value):
    return value if isinstance(value, list) else [value]

def entity_sequence(cif_path: Path, entity_id: str = "1") -> str:
    """Return the canonical one-letter sequence stored for an mmCIF polymer entity."""
    d = MMCIF2Dict(str(cif_path))
    ids = _as_list(d["_entity_poly.entity_id"])
    seqs = _as_list(d["_entity_poly.pdbx_seq_one_letter_code_can"])
    try:
        seq = seqs[ids.index(str(entity_id))]
    except ValueError as exc:
        raise ValueError(f"Entity {entity_id} not found") from exc
    return "".join(seq.split()).upper()
