from cisvis.spectra import generate_consensus_plot


def test_generate_consensus_plot(splash_test_name, cis_cli):
    library = splash_test_name[1]
    splash = splash_test_name[0]

    compound = cis_cli.get_compound(library=library, splash=splash)
    members = list(map(lambda member: cis_cli.get_compound(library=library, splash=member),
                       cis_cli.get_members(library=library, splash=splash)))
    generate_consensus_plot(members)
