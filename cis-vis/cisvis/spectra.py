from typing import List
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from pyspec.parser.pymzl.msms_spectrum import MSMSSpectrum
import matplotlib.pyplot as plt


def to_dataframe(compoud: List[dict]) -> DataFrame:
    """
    converts the incomming data to a dataframe
    :param compoud:
    :return:
    """
    dataframe = pd.DataFrame(compoud)

    def convert(x):
        return MSMSSpectrum(x.spectrum, precursor_mz=x.precursor_mass, name=x.id, record_id=x.splash)

    dataframe['spectrum'] = dataframe.apply(
        convert, axis=1)
    return dataframe


def generate_spectra_plot(compound: dict):
    """
    displays a simple spectra plot
    :param compound:
    :return:
    """
    pass


def generate_similarity_plot(compoud: List[dict], tolerance: float = 0.01, title: str = "similarity plot"):
    """
    this generates a similarity heatmap plot between all the compounds in the given list
    :param compoud:
    :param tolerance:
    :param title:
    :return:
    """
    dataframe = to_dataframe(compoud)
    spectra = dataframe['spectrum'].values

    data = []
    # compute simlarity matrix
    for first in spectra:
        for second in spectra:
            x: MSMSSpectrum = first
            y: MSMSSpectrum = second

            data.append({'x': x.name, 'y': y.name, 'score': x.spectral_similarity(y, tolerance=tolerance)})

    hm = pd.DataFrame(data)
    sns.heatmap(hm.pivot(index='x', columns='y', values='score'))

    plt.title(title)
    plt.show()
