"""Offline synthetic structures verify metrics independently of inference."""
from pathlib import Path
import numpy as np
import pytest
from Bio.PDB import Structure, Model, Chain, Residue, Atom, MMCIFIO
from urethanase_boltz2.evaluate import evaluate_complex


def make_cif(path, transform=False, shift=0, missing=False, sequence='AAS', ligand_offset=0):
    structure = Structure.Structure('fixture')
    model = Model.Model(0)
    structure.add(model)
    chain = Chain.Chain('A')
    model.add(chain)
    rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    serial = 0
    def add(residue, name, xyz, element):
        nonlocal serial
        coord = np.asarray(xyz, dtype=float)
        if transform:
            coord = coord @ rotation + [10, 20, -5]
        serial += 1
        residue.add(Atom.Atom(name, coord, 10, 1, ' ', name, serial, element=element))
    for i, (code, xyz) in enumerate(zip(sequence, [[0,0,0],[3,0,0],[0,3,0]]), 1):
        r = Residue.Residue((' ', i+shift, ' '), {'A':'ALA','S':'SER'}[code], '')
        chain.add(r)
        add(r, 'CA', xyz, 'C')
        if i == 2:
            add(r, 'CB', [3,0,1], 'C')
    ligand = Residue.Residue(('H_LIG', 501, ' '), 'LIG', '')
    chain.add(ligand)
    for name, xyz, element in [('C1',[3,0,2],'C'),('O1',[4,0,2],'O'),('N1',[3,1,2],'N')]:
        if not (missing and name == 'N1'):
            add(ligand,name,np.asarray(xyz)+[0,0,ligand_offset],element)
    io = MMCIFIO()
    io.set_structure(structure)
    io.save(str(path))
    from Bio.PDB.MMCIF2Dict import MMCIF2Dict
    data = MMCIF2Dict(str(path))
    data['_atom_site.label_entity_id'] = ['1' if v != '.' else '2' for v in data['_atom_site.label_seq_id']]
    io.set_dict(data)
    io.save(str(path))
    # MMCIFIO does not write entity sequence metadata.
    with path.open('a') as f:
        f.write(f'\nloop_\n_entity_poly.entity_id\n_entity_poly.pdbx_seq_one_letter_code_can\n1 {sequence}\n#\n')
    return path


def test_identity_and_rigid_transform_with_author_renumbering(tmp_path):
    ref = make_cif(tmp_path/'ref.cif')
    for transform, shift in [(False,0),(True,100)]:
        pred = make_cif(tmp_path/'pred.cif',transform=transform,shift=shift)
        m = evaluate_complex(ref,pred,'LIG',catalytic_residue=2)
        assert m['protein_ca_rmsd_angstrom'] < 1e-5
        assert m['ligand_pose_rmsd_angstrom'] < 1e-5
        assert m['contact_precision'] == m['contact_recall'] == 1
        assert m['reference_site_atom'] == 'CB'
        assert m['reference_site_anchor_to_ligand_min_distance_angstrom'] == pytest.approx(1)


def test_missing_ligand_atom_is_rejected(tmp_path):
    ref = make_cif(tmp_path/'ref.cif')
    pred = make_cif(tmp_path/'pred.cif',missing=True)
    with pytest.raises(ValueError,match='complete atom mapping'):
        evaluate_complex(ref,pred,'LIG',catalytic_residue=2)


def test_different_construct_is_rejected(tmp_path):
    ref = make_cif(tmp_path/'ref.cif')
    pred = make_cif(tmp_path/'pred.cif',sequence='SAS')
    with pytest.raises(ValueError,match='sequences differ'):
        evaluate_complex(ref,pred,'LIG',catalytic_residue=2)


def test_displaced_ligand_changes_pose_and_contacts(tmp_path):
    ref = make_cif(tmp_path/'ref.cif')
    pred = make_cif(tmp_path/'pred.cif',ligand_offset=10)
    m = evaluate_complex(ref,pred,'LIG',catalytic_residue=2)
    assert m['protein_ca_rmsd_angstrom'] < 1e-5
    assert m['ligand_pose_rmsd_angstrom'] == pytest.approx(10)
    assert m['contact_precision'] == m['contact_recall'] == 0
    assert m['predicted_site_anchor_to_ligand_min_distance_angstrom'] == pytest.approx(11)
