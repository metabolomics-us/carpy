from typing import List

from pyspec.loader.mona import MoNALoader


def identify_compound(compound: dict, min_similarity=0) -> List[dict]:
    """
    uses mona to search against a library to identify the given compounds
    with a list of possible matches based on a couple of basic assumptions
    :param compound:
    :return: a list with possible idnetifications
    """

    loader = MoNALoader()

    result = loader.similarity_serarch(compound['spectrum'], min_similarity=min_similarity,
                                       precursor_mz=compound['precursor_mass'], precursor_tolerance=0.1)

    def convert(hit, score):
        """
        converts a spectra to a compound dict

        :param spectra:
        :param similarity:
        :return:
        """
        return {
            'spectrum': hit.spectra,
            'name': hit.name,
            'id': hit.id,
            'inchi_key': hit.inchiKey,
            'splash': hit.splash,
            'score': score
        }

    result = list(map(lambda x: convert(x[0], x[1]), result))
    return result
