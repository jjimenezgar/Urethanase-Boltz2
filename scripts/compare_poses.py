"""Compare the original and closest sampled ligand poses in the protein frame."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from urethanase_boltz2.evaluate import (
    _active_site_ligand, _heavy_atoms, _structure, protein_ca_rmsd,
)

p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, default=Path('results/multiseed/pose_comparison.png'))
a = p.parse_args()
reference = Path('data/reference/8XTC.cif')
ref_atoms = _heavy_atoms(_active_site_ligand(_structure(reference), 'A1D5H', 'A'))
names = sorted(ref_atoms)
ref_xyz = np.array([ref_atoms[n].coord for n in names])
info = MMCIF2Dict(str(reference))
bonds = [(names.index(u), names.index(v))
         for component, u, v in zip(info['_chem_comp_bond.comp_id'],
                                    info['_chem_comp_bond.atom_id_1'],
                                    info['_chem_comp_bond.atom_id_2'])
         if component == 'A1D5H' and u in ref_atoms and v in ref_atoms]
poses = []
for seed, folder in [(42, Path('results/report')), (43, Path('results/multiseed/seeds/seed_43'))]:
    manifest = json.loads((folder/'manifest.json').read_text())
    prediction = Path(manifest['prediction'])
    _, alignment, _ = protein_ca_rmsd(reference, prediction)
    atoms = _heavy_atoms(_active_site_ligand(_structure(prediction), 'A1D5H', 'A'))
    xyz = np.array([atoms[n].coord for n in names]) @ alignment.rotran[0] + alignment.rotran[1]
    rmsd = json.loads((folder/'metrics.json').read_text())['ligand_pose_rmsd_angstrom']
    poses.append((seed, xyz, rmsd))
all_xyz = np.concatenate([ref_xyz, *(xyz for _, xyz, _ in poses)])
low, high = all_xyz.min(0)-1.5, all_xyz.max(0)+1.5
fig = plt.figure(figsize=(12,5.3), layout='constrained')
for index, ((seed, xyz, rmsd), color) in enumerate(zip(poses, ['#d76420', '#14845c']), 1):
    ax = fig.add_subplot(1,2,index,projection='3d')
    for points, tint in [(ref_xyz, '#1676b8'), (xyz, color)]:
        for u, v in bonds:
            ax.plot(*points[[u,v]].T, color=tint, linewidth=2)
        ax.scatter(*points.T, color=tint, s=28, depthshade=False)
    ax.set(xlim=(low[0],high[0]),ylim=(low[1],high[1]),zlim=(low[2],high[2]),
           xlabel='X (Å)',ylabel='Y (Å)',zlabel='Z (Å)',
           title=f'Seed {seed} · ligand RMSD {rmsd:.2f} Å')
    ax.set_box_aspect(high-low)
    ax.view_init(elev=22,azim=-55)
    ax.legend(handles=[Line2D([0],[0],color='#1676b8',label='8XTC reference',lw=2),
                       Line2D([0],[0],color=color,label=f'Boltz-2 seed {seed}',lw=2)],
              loc='upper left',fontsize=9)
fig.suptitle('Ligand poses after protein alignment', fontsize=15)
a.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(a.output,dpi=180)
plt.close(fig)
print(a.output)
