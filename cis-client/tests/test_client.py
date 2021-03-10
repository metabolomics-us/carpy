from time import time


def test_get_libraries(cis_cli):
    result = cis_cli.get_libraries()
    assert len(result) > 0


def test_exists_library(cis_cli, library_test_name):
    result = cis_cli.exists_library(library_test_name)
    assert result is True


def test_size_library(cis_cli, library_test_name):
    result = cis_cli.size_library(library_test_name)
    assert len(result) > 0


def test_get_compounds(cis_cli, splash_test_name):
    result = cis_cli.get_compounds(splash_test_name[1])
    assert len(result) > 0


def test_get_compounds_by_target_type(cis_cli, splash_test_name):
    result = cis_cli.get_compounds_by_type(splash_test_name[1], target_type="UNCONFIRMED")
    assert len(result) > 0


def test_get_compounds_by_target_type_2(cis_cli, splash_test_name):
    result = cis_cli.get_compounds_by_type(splash_test_name[1], target_type="UNCONFIRMED_CONSENSUS")
    assert len(result) > 0


def test_exists_compound(cis_cli, splash_test_name):
    result = cis_cli.exists_compound(library=splash_test_name[1], splash=splash_test_name[0])
    assert result is True


def test_get_compound(cis_cli, splash_test_name):
    result = cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])
    assert len(result) > 0


def test_set_compound_primary_name(cis_cli, splash_test_name):
    name = f"test-{time()}"
    result = cis_cli.set_compound_primary_name(library=splash_test_name[1], splash=splash_test_name[0], name=name)

    assert result['preferred_name'] == name
    assert len(result) > 0


def test_add_adduct(cis_cli, splash_test_name):
    test = f"test-{time()}"
    cis_cli.compound_add_adduct(library=splash_test_name[1], splash=splash_test_name[0], name=test,
                                identifiedBy="tester",
                                comment="")
    result = cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])

    success = False

    for name in result['associated_adducts']:
        if name['name'] == test:
            if name['identifiedBy'] == 'tester':
                success = True

    assert success


def test_add_adduct_and_remove(cis_cli, splash_test_name):
    test = f"test-{time()}"

    result = cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])
    print(result)
    for name in result['associated_adducts']:
        cis_cli.compound_remove_adduct(library=splash_test_name[1], splash=splash_test_name[0], name=name['name'],
                                       identifiedBy=name['identifiedBy'])

    assert len(cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])['associated_adducts']) == 0

    for name in result['associated_adducts']:
        cis_cli.compound_add_adduct(library=splash_test_name[1], splash=splash_test_name[0], name=test,
                                    identifiedBy="tester",
                                    comment="")

    result = cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])
    success = False

    for name in result['associated_adducts']:
        if name['name'] == test:
            if name['identifiedBy'] == 'tester':
                success = True

    assert success

    assert cis_cli.compound_remove_adduct(library=splash_test_name[1], splash=splash_test_name[0], name=test,
                                          identifiedBy='tester')


def test_name_compound(cis_cli, splash_test_name):
    cis_cli.name_compound(library=splash_test_name[1], splash=splash_test_name[0], name="test", identifiedBy="tester",
                          comment="")
    result = cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])

    success = False

    for name in result['associated_names']:
        if name['name'] == 'test':
            if name['identifiedBy'] == 'tester':
                success = True

    assert success


def test_delete_name_compound(cis_cli, splash_test_name):
    cis_cli.name_compound(library=splash_test_name[1], splash=splash_test_name[0], name="test", identifiedBy="tester",
                          comment="")
    result = cis_cli.get_compound(library=splash_test_name[1], splash=splash_test_name[0])

    success = False

    for name in result['associated_names']:
        if name['name'] == 'test':
            if name['identifiedBy'] == 'tester':
                success = True
    cis_cli.delete_name_compound(library=splash_test_name[1], splash=splash_test_name[0], name="test",
                                 identifiedBy="tester")
    assert success


def test_get_members_false(cis_cli, splash_test_name):
    result = cis_cli.get_members(library=splash_test_name[1], splash="{}_nodice".format(splash_test_name[0]))
    assert len(result) == 0


def test_get_members(cis_cli, splash_test_name_with_members):
    result = cis_cli.get_members(library=splash_test_name_with_members[1], splash=splash_test_name_with_members[0])
    assert len(result) > 0

    for x in result:
        print(x)


def test_get_target_profiles(cis_cli, target_id):
    result = cis_cli.get_profiles('target', target_id)
    assert len(result['profiles']) > 0

    assert [363, 'carrot.filters.similarity'] in result['profiles']


def test_get_target_configs(cis_cli, target_id):
    result = cis_cli.get_configs('target', target_id)
    assert len(result['configs']) > 0

    assert [362, 'CARROT_METHOD', 'soqtof[M-H] | 6530a | c18 | negative', 'java.lang.String', ''] in result['configs']


def test_get_sample_profiles(cis_cli, sample_id):
    result = cis_cli.get_profiles('sample', sample_id)
    assert len(result['profiles']) > 0

    assert [8395, 'carrot.filters.similarity'] in result['profiles']


def test_get_sample_configs(cis_cli, sample_id):
    result = cis_cli.get_configs('sample', sample_id)
    assert len(result['configs']) > 0

    assert [8302, 'wcmc.workflow.replacement.enabled', 'true', 'java.lang.Boolean',
            'edu.ucdavis.fiehnlab.ms.carrot.core.workflow.sample.postprocessing.ZeroReplacementProperties'] \
           in result['configs']
