from __future__ import annotations

from pathlib import Path
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.SeqUtils import seq1

def _as_list(value):
    return value if isinstance(value, list) else [value]

def polymer_sequences(d: dict) -> dict[str, str]:
    """Read complete polymer identity, including ModelCIF's all-X canonical strings."""
    ids = _as_list(d["_entity_poly.entity_id"])
    seqs = _as_list(d["_entity_poly.pdbx_seq_one_letter_code_can"])
    result = {i: "".join(s.split()).upper() for i, s in zip(ids, seqs)}
    if "_entity_poly_seq.mon_id" in d:
        by_entity = {}
        for entity, number, monomer in zip(
            _as_list(d["_entity_poly_seq.entity_id"]),
            _as_list(d["_entity_poly_seq.num"]),
            _as_list(d["_entity_poly_seq.mon_id"]),
        ):
            by_entity.setdefault(entity, {})[int(number)] = seq1(monomer)
        for entity, positions in by_entity.items():
            reconstructed = "".join(positions[i] for i in sorted(positions))
            canonical = result[entity]
            if "X" in canonical and "X" not in reconstructed:
                if sorted(positions) != list(range(1, len(canonical)+1)):
                    raise ValueError("Incomplete polymer sequence table")
                if any(c != "X" and c != r for c, r in zip(canonical, reconstructed)):
                    raise ValueError("Inconsistent polymer sequence metadata")
                result[entity] = reconstructed
    return result


def entity_sequence(cif_path: Path, entity_id: str = "1") -> str:
    """Return the complete deposited polymer sequence for an entity."""
    sequences = polymer_sequences(MMCIF2Dict(str(cif_path)))
    try:
        return sequences[str(entity_id)]
    except KeyError as exc:
        raise ValueError(f"Entity {entity_id} not found") from exc
