"""Lightweight Hyperion coordinator: never submit above two active user test jobs."""
import fcntl
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path('/scratch/jcjimenez/Urethanase-Boltz2-benchmark')
import os
os.chdir(root)
os.environ.setdefault("XDG_CACHE_HOME", str(root/".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(root/".cache/matplotlib"))
out = Path('results/multiseed')
out.mkdir(parents=True,exist_ok=True)
lock = (out/'controller.lock').open('w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
state_path = out/'controller_status.json'
state = json.loads(state_path.read_text()) if state_path.exists() else {
    'jobs':{'batch_1':'7693078','batch_2':'7693079'},'status':'waiting',
    'seeds':[42,43,44,45,46,47,48,49,50,51]}
def command(args):
    return subprocess.check_output(args,text=True).strip()
def save():
    state['updated_utc'] = datetime.now(timezone.utc).isoformat()
    temporary = state_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.replace(state_path)
try:
    deadline=time.monotonic()+48*3600
    while time.monotonic()<deadline:
        active=command(['squeue','-h','-u','jcjimenez','-q','test','-o','%i %T']).splitlines()
        state['active_user_test_jobs']=active
        if 'batch_3' not in state['jobs'] and len(active)<2:
            job=command(['sbatch','--parsable','--job-name=urethanase-seeds-49-51','cluster/seed_batch.sbatch','49','50','51']).split(';')[0]
            state['jobs']['batch_3']=job
            save()
        states={}
        for name,job in state['jobs'].items():
            rows=command(['sacct','-n','-X','-j',job,'--format=State','--parsable2']).splitlines()
            states[name]=rows[0].strip().split('|')[0] if rows else 'UNKNOWN'
        state['job_states']=states
        state['status']='waiting_or_running'
        save()
        terminal={'COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY','PREEMPTED','BOOT_FAIL','DEADLINE'}
        if len(states)==3 and all(v.split()[0] in terminal for v in states.values()):
            if not all(v=='COMPLETED' for v in states.values()):
                raise RuntimeError(f'One or more batches did not complete: {states}')
            break
        time.sleep(30)
    else:
        raise TimeoutError('Coordinator stopped after 48 hours')
    state['status']='collecting';save()
    for seed in range(43,52):
        source=Path(f'results/seeds/seed_{seed}')
        manifest=json.loads((source/'manifest.json').read_text())
        if manifest['status']!='complete':raise RuntimeError(f'Seed {seed} incomplete')
        prediction=Path(manifest['prediction'])
        if hashlib.sha256(prediction.read_bytes()).hexdigest()!=manifest['prediction_sha256']:
            raise RuntimeError(f'Seed {seed} checksum mismatch')
        target=out/'seeds'/f'seed_{seed}';target.mkdir(parents=True,exist_ok=True)
        dest=Path(f'data/predictions/seed_{seed}.cif');dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(prediction,dest)
        manifest['original_prediction']=manifest['prediction'];manifest['prediction']=str(dest)
        (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        shutil.copy2(source/'metrics.json',target/'metrics.json')
        confidences=list(prediction.parent.glob('confidence_*_model_0.json'))
        if len(confidences)!=1:raise RuntimeError(f'Seed {seed} confidence file missing')
        shutil.copy2(confidences[0],target/'confidence.json')
    log_folder=out/'logs';log_folder.mkdir(exist_ok=True)
    for job in state['jobs'].values():shutil.copy2(f'logs/seeds-{job}.log',log_folder)
    subprocess.run(['.venv/bin/python','scripts/summarize_seeds.py'],check=True)
    state['status']='complete';save()
    files=[p for p in out.rglob('*') if p.is_file() and p.name not in ('controller.lock','artifacts.sha256')]
    files += list(Path('data/predictions').glob('seed_*.cif'))
    (out/'artifacts.sha256').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n' for p in sorted(files)))
    subprocess.run(['tar','-czf','multiseed-completed.tar.gz',str(out),*[str(p) for p in Path('data/predictions').glob('seed_*.cif')]],check=True)
    (out/'download_ready').write_text('complete\n')
except Exception as exc:
    state['status']='failed';state['error']=str(exc);save()
    raise
