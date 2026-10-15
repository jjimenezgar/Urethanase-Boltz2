"""Retrieve the completed lightweight seed bundle, optionally waiting for it."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import time

p=argparse.ArgumentParser()
p.add_argument('--watch',action='store_true')
a=p.parse_args()
host='jcjimenez@hyperion.sw.ehu.es'
remote='/scratch/jcjimenez/Urethanase-Boltz2-benchmark'
root=Path(__file__).resolve().parents[1]
deadline=time.monotonic()+48*3600
while True:
    result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20',host,
        f'cat {remote}/results/multiseed/controller_status.json'],capture_output=True,text=True,timeout=60)
    if result.returncode==0:
        state=json.loads(result.stdout)
        (root/'results/multiseed/remote_status.json').write_text(json.dumps(state,indent=2)+'\n')
        if state['status']=='failed':raise SystemExit(state.get('error','Remote controller failed'))
        if state['status']=='complete':
            ready=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20',host,
                f'test -f {remote}/results/multiseed/download_ready'],timeout=60)
            if ready.returncode==0:break
    if not a.watch:
        raise SystemExit('Results are not ready; inspect results/multiseed/remote_status.json')
    if time.monotonic()>=deadline:raise SystemExit('Stopped waiting after 48 hours')
    time.sleep(30)
with tempfile.TemporaryDirectory(prefix='urethanase-seeds-') as temp:
    archive=Path(temp)/'results.tar.gz'
    subprocess.run(['scp','-q',f'{host}:{remote}/multiseed-completed.tar.gz',str(archive)],check=True,timeout=120)
    with tarfile.open(archive) as tar:
        for member in tar:
            name=Path(member.name)
            allowed=member.name.startswith('results/multiseed/') or (name.parent==Path('data/predictions') and name.name.startswith('seed_') and name.suffix=='.cif')
            if member.name=='results/multiseed':continue
            if not allowed or '..' in name.parts or name.is_absolute() or not (member.isfile() or member.isdir()):
                raise ValueError(f'Unexpected archive member: {member.name}')
            dest=root/name
            if member.isdir():dest.mkdir(parents=True,exist_ok=True)
            else:
                dest.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as source:dest.write_bytes(source.read())
for line in (root/'results/multiseed/artifacts.sha256').read_text().splitlines():
    expected,name=line.split('  ',1)
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise ValueError(f'Checksum mismatch: {name}')
print('Downloaded and verified:',root/'results/multiseed/report.md',flush=True)
