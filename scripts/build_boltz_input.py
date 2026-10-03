from pathlib import Path
from urethanase_boltz2.structure import entity_sequence
from urethanase_boltz2.boltz_input import write_boltz_yaml

if __name__ == "__main__":
    ref = Path("data/reference/8XTC.cif")
    if not ref.exists():
        raise SystemExit("Run scripts/fetch_reference.py first")
    sequence = entity_sequence(ref, "1")
    out = write_boltz_yaml(sequence, "A1D5H", Path("inputs/umg_sp2_a1d5h.yaml"))
    print(f"Wrote {out} ({len(sequence)} aa)")
