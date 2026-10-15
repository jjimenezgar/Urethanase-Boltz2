import pytest
from urethanase_boltz2.structure import polymer_sequences


def test_modelcif_unknown_canonical_sequence_uses_monomer_table():
    d = {'_entity_poly.entity_id':['1'], '_entity_poly.pdbx_seq_one_letter_code_can':['XXX'],
         '_entity_poly_seq.entity_id':['1','1','1'], '_entity_poly_seq.num':['1','2','3'],
         '_entity_poly_seq.mon_id':['ALA','ALA','SER']}
    assert polymer_sequences(d)['1'] == 'AAS'
    d['_entity_poly.pdbx_seq_one_letter_code_can'] = ['SXX']
    with pytest.raises(ValueError,match='Inconsistent'):
        polymer_sequences(d)


def test_incomplete_modelcif_sequence_table_is_rejected():
    d = {'_entity_poly.entity_id':['1'], '_entity_poly.pdbx_seq_one_letter_code_can':['XXX'],
         '_entity_poly_seq.entity_id':['1','1'], '_entity_poly_seq.num':['1','3'],
         '_entity_poly_seq.mon_id':['ALA','SER']}
    with pytest.raises(ValueError,match='Incomplete'):
        polymer_sequences(d)
