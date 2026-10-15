"""Export an aligned ligand figure and a metric table from a completed run."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from urethanase_boltz2.evaluate import _structure, _active_site_ligand, _heavy_atoms, protein_ca_rmsd

p=argparse.ArgumentParser()
p.add_argument('--run-dir',type=Path,required=True)
p.add_argument('--output',type=Path,default=Path('results/report'))
a=p.parse_args()
m=json.loads((a.run_dir/'metrics.json').read_text())
manifest=json.loads((a.run_dir/'manifest.json').read_text())
if manifest['status'] != 'complete':
    raise SystemExit('A completed run is required')
ref=Path('data/reference/8XTC.cif')
pred=Path(manifest['prediction'])
_,sup,_=protein_ca_rmsd(ref,pred)
r=_heavy_atoms(_active_site_ligand(_structure(ref),'A1D5H','A'))
s=_heavy_atoms(_active_site_ligand(_structure(pred),'A1D5H','A'))
names=sorted(r)
rxyz=np.array([r[n].coord for n in names])
sxyz=np.array([s[n].coord for n in names]) @ sup.rotran[0] + sup.rotran[1]
a.output.mkdir(parents=True,exist_ok=True)
fig=plt.figure(figsize=(8,6)); ax=fig.add_subplot(projection='3d')
ax.scatter(*rxyz.T,label='8XTC reference',color='#1676b8')
ax.scatter(*sxyz.T,label='Boltz-2 prediction',color='#dc6c21')
for i,n in enumerate(names):
    ax.plot(*np.stack([rxyz[i],sxyz[i]]).T,color='gray',alpha=.35,linewidth=.7)
ax.set(xlabel='X (Å)',ylabel='Y (Å)',zlabel='Z (Å)',title='Ligand heavy atoms after protein alignment')
ax.legend();fig.tight_layout();fig.savefig(a.output/'ligand_overlay.png',dpi=200);plt.close(fig)
rows=[('Protein Cα RMSD (Å)',m['protein_ca_rmsd_angstrom']),('Ligand pose RMSD (Å)',m['ligand_pose_rmsd_angstrom']),('Contact precision',m['contact_precision']),('Contact recall',m['contact_recall']),('Reference ALA190 CB distance (Å)',m['reference_site_anchor_to_ligand_min_distance_angstrom']),('Predicted site-marker distance (Å)',m['predicted_site_anchor_to_ligand_min_distance_angstrom'])]
text='# Boltz-2 / 8XTC result\n\n| Metric | Value |\n|---|---:|\n'
text+=''.join(f'| {k} | {v:.4f} |\n' for k,v in rows)
text+=f'\n![Aligned ligand heavy atoms](ligand_overlay.png)\n\nOne sample, seed {manifest.get("seed", "unknown")}; no reference-based ranking. Distances use ALA190 CB, not a catalytic hydroxyl. Ligand RMSD uses CCD names without symmetry correction. This retrospective result does not establish prospective generalization or catalytic activity.\n'
(a.output/'report.md').write_text(text)
for name in ['metrics.json','manifest.json']:
    (a.output/name).write_bytes((a.run_dir/name).read_bytes())
print(a.output/'report.md')
