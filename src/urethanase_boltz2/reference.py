from __future__ import annotations

from pathlib import Path
import requests

RCSB_CIF = "https://files.rcsb.org/download/{pdb_id}.cif"


def download_cif(pdb_id: str, output: Path) -> Path:
    """Download an experimental mmCIF file from RCSB PDB."""
    pdb_id = pdb_id.upper()
    response = requests.get(RCSB_CIF.format(pdb_id=pdb_id), timeout=60)
    response.raise_for_status()
    if not response.text.lstrip().startswith("data_"):
        raise ValueError("Downloaded file does not look like mmCIF")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(response.text)
    return output
