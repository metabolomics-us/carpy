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


def test_get_members(cis_cli, splash_test_name):
    result = cis_cli.get_members(library=splash_test_name[1], splash=splash_test_name[0])
    assert len(result) > 0

    for x in result:
        print(x)
