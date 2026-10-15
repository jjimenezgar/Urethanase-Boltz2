"""Summarize every predeclared seed without selecting by experimental accuracy."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from urethanase_boltz2.evaluate import _structure, _active_site_ligand, _heavy_atoms, protein_ca_rmsd

p = argparse.ArgumentParser()
p.add_argument('--root', type=Path, default=Path('results/multiseed'))
a = p.parse_args()
plan = json.loads((a.root/'plan.json').read_text())
seeds = [plan['baseline_seed'], *plan['additional_seeds']]
rows, coordinates = [], []
reference = Path('data/reference/8XTC.cif')
for seed in seeds:
    folder = Path('results/report') if seed == plan['baseline_seed'] else a.root/'seeds'/f'seed_{seed}'
    manifest = json.loads((folder/'manifest.json').read_text())
    if manifest['status'] != 'complete' or manifest['seed'] != seed:
        raise ValueError(f'Seed {seed} is not complete')
    prediction = Path(manifest['prediction'])
    if hashlib.sha256(prediction.read_bytes()).hexdigest() != manifest['prediction_sha256']:
        raise ValueError(f'Prediction hash mismatch: {seed}')
    metrics = json.loads((folder/'metrics.json').read_text())
    confidence = json.loads((folder/'confidence.json').read_text())
    rows.append({'seed':seed,
                 'protein_ca_rmsd_angstrom':metrics['protein_ca_rmsd_angstrom'],
                 'ligand_pose_rmsd_angstrom':metrics['ligand_pose_rmsd_angstrom'],
                 'contact_precision':metrics['contact_precision'],
                 'contact_recall':metrics['contact_recall'],
                 'confidence_score':confidence['confidence_score'],
                 'ligand_iptm':confidence['ligand_iptm']})
    _, alignment, _ = protein_ca_rmsd(reference, prediction)
    atoms = _heavy_atoms(_active_site_ligand(_structure(prediction), 'A1D5H', 'A'))
    coordinates.append(np.array([atoms[n].coord for n in sorted(atoms)]) @ alignment.rotran[0] + alignment.rotran[1])
with (a.root/'seeds.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
summary = {'seed_count':len(rows), 'seeds':seeds, 'statistics':{},
           'interpretation_limit':'Ten samples from one construct; no prospective generalization or success-rate claim',
           'pose_distance_definition':'CCD atom-name RMSD after each protein is aligned to reference; no symmetry correction'}
for metric in list(rows[0])[1:]:
    values = np.array([r[metric] for r in rows])
    summary['statistics'][metric] = {'min':float(values.min()), 'median':float(np.median(values)),
                                   'max':float(values.max()), 'mean':float(values.mean()),
                                   'sample_std':float(values.std(ddof=1)),
                                   'q25':float(np.quantile(values,.25)), 'q75':float(np.quantile(values,.75))}
coords = np.asarray(coordinates)
distances = np.sqrt(np.mean(np.sum((coords[:,None]-coords[None,:])**2,axis=-1),axis=-1))
summary['pairwise_ligand_rmsd_angstrom'] = distances.tolist()
(a.root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
fig, axes = plt.subplots(1,3,figsize=(15,4.5),layout='constrained')
axes[0].bar([str(s) for s in seeds], [r['ligand_pose_rmsd_angstrom'] for r in rows],color=['#dc6c21']+['#1676b8']*(len(seeds)-1))
axes[0].set(xlabel='Seed (42: original run)',ylabel='Ligand RMSD to experiment (Å)',title='All predeclared seeds')
axes[1].scatter([r['confidence_score'] for r in rows],[r['ligand_pose_rmsd_angstrom'] for r in rows],color='#1676b8')
for r in rows:
    axes[1].annotate(str(r['seed']),(r['confidence_score'],r['ligand_pose_rmsd_angstrom']),xytext=(3,3),textcoords='offset points',fontsize=8)
axes[1].set(xlabel='Boltz confidence score',ylabel='Ligand RMSD to experiment (Å)',title='Confidence versus observed error')
im = axes[2].imshow(distances,cmap='viridis',vmin=0)
axes[2].set(xticks=range(len(seeds)),xticklabels=seeds,yticks=range(len(seeds)),yticklabels=seeds,xlabel='Seed',ylabel='Seed',title='Pairwise ligand pose RMSD')
fig.colorbar(im,ax=axes[2],label='Å')
fig.savefig(a.root/'seed_comparison.png',dpi=160);plt.close(fig)
text = '# Ten-seed benchmark\n\nAll ten predeclared seeds are included. The original seed 42 used the MSA server; the other nine used the exact saved MSA. All runs use one sample, three recycles and 200 diffusion steps.\n\n'
text += '| Seed | Protein RMSD (Å) | Ligand RMSD (Å) | Contact precision | Contact recall | Confidence |\n|---|---:|---:|---:|---:|---:|\n'
for r in rows:
    text += f"| {r['seed']} | {r['protein_ca_rmsd_angstrom']:.3f} | {r['ligand_pose_rmsd_angstrom']:.3f} | {r['contact_precision']:.3f} | {r['contact_recall']:.3f} | {r['confidence_score']:.3f} |\n"
s = summary['statistics']['ligand_pose_rmsd_angstrom']
text += f"\nLigand RMSD: median **{s['median']:.3f} Å**, range **{s['min']:.3f}–{s['max']:.3f} Å**, interquartile range **{s['q25']:.3f}–{s['q75']:.3f} Å**.\n\n"
text += '![Seed comparison](seed_comparison.png)\n\nPairwise distances use the protein-aligned coordinates and CCD atom names. No symmetry correction or post hoc pose-clustering threshold is applied. The lowest RMSD is a retrospective diagnostic, not a prospectively selected prediction. Ten samples do not establish a general success rate.\n'
(a.root/'report.md').write_text(text)
print(json.dumps(summary['statistics'],indent=2))
