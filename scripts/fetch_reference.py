from pathlib import Path
from urethanase_boltz2.reference import download_cif

if __name__ == "__main__":
    path = download_cif("8XTC", Path("data/reference/8XTC.cif"))
    print(f"Downloaded {path}")
