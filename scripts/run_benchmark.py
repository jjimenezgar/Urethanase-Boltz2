"""Run a fixed Boltz-2 protocol and record provenance before evaluation."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import yaml
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from urethanase_boltz2.evaluate import evaluate_complex, save_metrics

p = argparse.ArgumentParser()
p.add_argument('--out-dir', type=Path, required=True)
p.add_argument('--seed', type=int, default=42)
p.add_argument('--input', type=Path, default=Path('inputs/umg_sp2_a1d5h.yaml'))
p.add_argument('--evaluate-only', action='store_true', help='Evaluate an existing run without repeating inference')
a = p.parse_args()
if not a.evaluate_only and list(a.out_dir.rglob('*_model_0.cif')):
    raise SystemExit('Output already contains predictions; use a fresh output directory')
a.out_dir.mkdir(parents=True, exist_ok=True)
reference = Path('data/reference/8XTC.cif')
input_path = a.input
input_doc = yaml.safe_load(input_path.read_text())
needs_msa_server = any('protein' in entry and 'msa' not in entry['protein'] for entry in input_doc['sequences'])
command = ['boltz', 'predict', str(input_path), '--model', 'boltz2',
           '--out_dir', str(a.out_dir), '--seed', str(a.seed),
           '--no_kernels', '--diffusion_samples', '1', '--recycling_steps', '3',
           '--sampling_steps', '200', '--cache', str(Path('.cache/boltz').resolve())]
if needs_msa_server:
    command.append('--use_msa_server')
versions = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
manifest = {'started_utc': datetime.now(timezone.utc).isoformat(), 'command':command,
            'python':sys.version, 'seed':a.seed, 'versions':versions, 'slurm_job_id':os.getenv('SLURM_JOB_ID'),
            'sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [reference,input_path,Path('src/urethanase_boltz2/evaluate.py'),Path(__file__)]},
            'prediction_selection':'single sample model_0; no reference-based ranking',
            'msa_mode':'server' if needs_msa_server else 'fixed input MSA',
            'status':'running'}
manifest_path = a.out_dir/'manifest.json'
def write_manifest():
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
if a.evaluate_only:
    manifest = json.loads(manifest_path.read_text())
    if 'error' in manifest:
        manifest['previous_pipeline_error'] = manifest.pop('error')
    manifest['evaluation_command'] = [sys.executable, *sys.argv]
    manifest['evaluation_code_sha256'] = hashlib.sha256(Path('src/urethanase_boltz2/evaluate.py').read_bytes()).hexdigest()
    manifest['sequence_code_sha256'] = hashlib.sha256(Path('src/urethanase_boltz2/structure.py').read_bytes()).hexdigest()
    manifest['status'] = 'evaluating'
write_manifest()
try:
    if not a.evaluate_only:
        subprocess.run(command, check=True)
    predictions = list(a.out_dir.rglob(f'{input_path.stem}_model_0.cif'))
    if len(predictions) != 1:
        raise RuntimeError(f'Expected exactly one model_0 CIF, found {len(predictions)}')
    prediction = predictions[0]
    metrics = evaluate_complex(reference, prediction, 'A1D5H')
    save_metrics(metrics,a.out_dir/'metrics.json')
    manifest.update(status='complete', prediction=str(prediction),
                    prediction_sha256=hashlib.sha256(prediction.read_bytes()).hexdigest())
except Exception as exc:
    manifest.update(status='failed', error=str(exc))
    raise
finally:
    manifest['finished_utc'] = datetime.now(timezone.utc).isoformat()
    write_manifest()

subprocess.run([sys.executable, 'scripts/report_benchmark.py', '--run-dir', str(a.out_dir), '--output', str(a.out_dir/'report')], check=True)
