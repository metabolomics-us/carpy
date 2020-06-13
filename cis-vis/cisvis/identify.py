from typing import List


def identify_compound(compound: dict) -> List[dict]:
    """
    uses mona to search against a library to identify the given compounds
    with a list of possible matches based on a couple of basic assumptions
    :param compound:
    :return: a list with possible idnetifications
    """
