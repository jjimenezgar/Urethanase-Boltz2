"""Package only the curated project files; never include Git metadata or caches."""
import argparse
from pathlib import Path
import zipfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, default=Path('dist/urethanase-boltz2-github-update.zip'))
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
files = {root/name for name in ['README.md','LICENSE','CHANGELOG.md','.gitignore','.gitattributes',
                               'pyproject.toml','pytest.ini','artifacts.sha256']}
folders = ['.github','src','tests','scripts','docs','notebooks','cluster','inputs',
           'data/reference','data/predictions','data/msa','results/report',
           'results/multiseed','results/validation']
files.add(root/'data/README.md')
for folder in folders:
    files.update(p for p in (root/folder).rglob('*') if p.is_file())
files.add(root/'results/.gitkeep')
exclude = {'__pycache__','.pytest_cache','controller.lock','remote_status.json',
           'download.log','download_ready'}
files = sorted(p for p in files if not exclude.intersection(p.relative_to(root).parts)
               and p.suffix not in {'.pyc','.pyo'}
               and not (p.parent == root/'data/msa' and p.suffix == '.csv'))
output = a.output if a.output.is_absolute() else root/a.output
output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for path in files:
        archive.write(path,path.relative_to(root).as_posix())
print(f'{output}: {len(files)} files, {output.stat().st_size:,} bytes compressed; '
      f'{sum(p.stat().st_size for p in files):,} bytes unpacked')
