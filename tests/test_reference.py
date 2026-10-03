from pathlib import Path
import pytest
from urethanase_boltz2.reference import download_cif

@pytest.mark.integration
def test_download_8xtc(tmp_path):
    path = download_cif("8XTC", tmp_path / "8XTC.cif")
    assert path.read_text().startswith("data_8XTC")
