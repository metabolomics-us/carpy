import sys

import pytest
from loguru import logger

from similarity_client.similarity import Similarity

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_similarity", level="INFO", backtrace=False,
           diagnose=False)

client = Similarity("https://preview.fiehnlab.ucdavis.edu")


def test_get_all_similarities(splash_pair):
    result = client.get_all_similarities(splash_pair['unk'], splash_pair['ref'])


def test_get_all_bad_splash(splash_pair):
    with pytest.raises(Exception):
        client.get_all_similarities("splash_pair['unk']", splash_pair['ref'])


def test_get_entropy_similarity(spectrum_pair):
    result = client.get_entropy_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_entropy_similarity_bad_param(spectrum_pair):
    with pytest.raises(Exception):
        result = client.get_entropy_similarity(spectrum_pair['unk'], "blah")


def test_get_weighted_entropy_similarity(spectrum_pair):
    result = client.get_weighted_entropy_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_total_similarity(spectrum_pair):
    result = client.get_total_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_cosine_similarity(spectrum_pair):
    result = client.get_cosine_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_reverse_similarity(spectrum_pair):
    result = client.get_reverse_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_presence_similarity(spectrum_pair):
    result = client.get_presence_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_nominal_cosine_similarity(spectrum_pair):
    result = client.get_nominal_cosine_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_composite_similarity(spectrum_pair):
    result = client.get_composite_similarity(spectrum_pair['unk'], spectrum_pair['ref'])
