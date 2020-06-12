from cisvis.spectra import generate_similarity_plot, generate_histogram_intensity, generate_histogram_ri, \
    generate_histogram_accurate_mass, generate_similarity_histogram


def test_generate_similarity_plot(members):
    generate_similarity_plot(members)


def test_generate_histogram_accuramte_mass(members):
    generate_histogram_accurate_mass(members)


def test_generate_histogram_ri(members):
    generate_histogram_ri(members)


def test_generate_histogram_intensity(members):
    generate_histogram_intensity(members)


def test_generate_similarity_histogram(compound, members):
    generate_similarity_histogram(compound, members)
