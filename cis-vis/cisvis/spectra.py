from typing import List, Optional
import pandas as pd
import seaborn as sns
from matplotlib import ticker
from pandas import DataFrame
from pyspec.parser.pymzl.msms_spectrum import MSMSSpectrum
import matplotlib.pyplot as plt
from pyspec.plot.plot_mass_spectrum import _plot_spectrum, plot_mass_spectrum


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
    plot_mass_spectrum(compound['spectrum'])
    plt.show()


def generate_histogram_accurate_mass(compound: List[dict], title: str = "accurate mass distribution"):
    def function(x: dict):
        return x['accurate_mass']

    generate_histogram(compound, function, title, label_x="accurate mass", format='{:,.4f}')


def generate_histogram_ri(compound: List[dict], title: str = "retention index distribution"):
    def function(x: dict):
        return x['retention_index']

    generate_histogram(compound, function, title, label_x="retention index", format='{:,.2f}')


def generate_histogram_intensity(compound: List[dict], title: str = "intensity distribution"):
    def function(x: dict):
        spec: MSMSSpectrum = MSMSSpectrum(x['spectrum'])
        highest = spec.highestPeaks(1)[0, 1]

        return highest

    generate_histogram(compound, function, title, label_x="intensity", format='{:,.0f}')


def generate_histogram(compound: List[dict], aggregateFunction, tile: str = "histogram", label_x: str = "x",
                       label_y: str = "y", format: Optional[str] = None):
    x = list(map(aggregateFunction, compound))
    p = sns.distplot(x)

    p.set(xlabel=label_x, ylabel=label_y)
    if format is not None:
        p.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: format.format(x)))

    plt.title(tile)

    plt.show()


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
