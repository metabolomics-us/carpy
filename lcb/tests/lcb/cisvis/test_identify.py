from lcb.cisvis.identify import identify_compound


def test_identify_compound_nothing_found(compound):
    result = identify_compound(compound)

    assert len(result) == 0


def test_identify_compound_something_found(compound_with_sim_hits):
    result = identify_compound(compound_with_sim_hits)

    assert len(result) > 0


def test_identify_compound_something_found(compound_with_sim_hits2):
    result = identify_compound(compound_with_sim_hits2)

    assert len(result) > 0
