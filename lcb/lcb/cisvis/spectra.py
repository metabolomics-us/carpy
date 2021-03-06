from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import ticker
from pandas import DataFrame
from pyspec.parser.pymzl.msms_spectrum import MSMSSpectrum
from pyspec.plot.plot_mass_spectrum import plot_mass_spectrum, plot_head_to_tail_mass_spectra


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


def generate_head_tail_plot(compound: dict, member: dict,figsize):
    plot_head_to_tail_mass_spectra(member['spectrum'], compound['spectrum'],
                                   title="id: {}. sample: {}".format(member['id'], member['sample']),figsize=figsize)
    plt.show()


def generate_histogram_accurate_mass(compound: List[dict], title: str = "accurate mass distribution", axes=None):
    def function(x: dict):
        return x['accurate_mass']

    generate_histogram(compound, function, title, label_x="accurate mass", format='{:,.4f}', axes=axes)


def generate_histogram_ri(compound: List[dict], title: str = "retention index distribution", axes=None):
    def function(x: dict):
        return x['retention_index']

    generate_histogram(compound, function, title, label_x="retention index", format='{:,.2f}', axes=axes)


def generate_histogram_intensity(compound: List[dict], title: str = "intensity distribution", axes=None):
    def function(x: dict):
        spec: MSMSSpectrum = MSMSSpectrum(x['spectrum'])
        highest = spec.highestPeaks(1)[0, 1]

        return highest

    generate_histogram(compound, function, title, label_x="intensity", format='{:,.0f}', axes=axes)


def generate_histogram(compound: List[dict], aggregateFunction, tile: str = "histogram", label_x: str = "x",
                       label_y: str = "count", format: Optional[str] = None, axes=None):
    try:
        if axes is None:
            show = True
            f, axes = plt.subplots(
            )
        else:
            show = False
        x = list(map(aggregateFunction, compound))
        p = sns.distplot(x, ax=axes)

        p.set(xlabel=label_x, ylabel=label_y)
        if format is not None:
            p.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: format.format(x)))

        plt.title(tile)
        for tick in axes.get_xticklabels():
            tick.set_rotation(45)

        if show:
            plt.show()

    except Exception as e:
        print(e)


def generate_similarity_plot(compoud: List[dict], tolerance: float = 0.01, title: str = "similarity plot", axes=None):
    """
    this generates a similarity heatmap plot between all the compounds in the given list
    :param compoud:
    :param tolerance:
    :param title:
    :return:
    """

    try:
        dataframe = to_dataframe(compoud)
        spectra = dataframe['spectrum'].values

        data = []
        # compute simlarity matrix
        for first in spectra:
            for second in spectra:
                x: MSMSSpectrum = first
                y: MSMSSpectrum = second

                data.append({'x (spectra id)': x.name, 'y (spectra id)': y.name, 'score': x.spectral_similarity(y, tolerance=tolerance)})

        if axes is None:
            f, axes = plt.subplots()
        hm = pd.DataFrame(data)
        sns.heatmap(data=hm.pivot(index='x (spectra id)', columns='y (spectra id)', values='score'), ax=axes)

        plt.title(title)
        plt.show()
        return hm
    except Exception as e:
        print(e)


def generate_similarity_histogram(consensus: dict, compoud: List[dict], tolerance: float = 0.01,
                                  title: str = "similarity histogram plot", axes=None):
    """
    this generates a similarity heatmap plot between all the compounds in the given list
    :param compoud:
    :param tolerance:
    :param title:
    :return:
    """
    dataframe = to_dataframe(compoud)
    spectra = dataframe['spectrum'].values

    y = consensus['spectrum']
    data = []
    # compute simlarity histogram of all members against the concensus
    for x in spectra:
        data.append(x.spectral_similarity(y, tolerance=tolerance))
    if axes is None:
        f, axes = plt.subplots()
    p = sns.distplot(data, ax=axes)

    p.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: "{:,.3f}".format(x)))

    plt.title(title)
    plt.show()
