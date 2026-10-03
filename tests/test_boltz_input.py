import yaml
import pytest
from urethanase_boltz2.boltz_input import write_boltz_yaml


def test_writes_minimal_complex(tmp_path):
    out = write_boltz_yaml("ACDEFGHIK", "A1D5H", tmp_path / "input.yaml")
    doc = yaml.safe_load(out.read_text())
    assert doc["version"] == 1
    assert doc["sequences"][0]["protein"]["id"] == "A"
    assert doc["sequences"][1]["ligand"]["ccd"] == "A1D5H"


def test_rejects_noncanonical_sequence(tmp_path):
    with pytest.raises(ValueError):
        write_boltz_yaml("ACDX", "A1D5H", tmp_path / "input.yaml")
