import sys

from similarity_client.similarity import Similarity
from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_similarity", level="INFO", backtrace=False,
           diagnose=False)

client = Similarity("https://preview.fiehnlab.ucdavis.edu")


def test_get_all_similarities(splash_pair):
    client.get_all_similarities(splash_pair['unk'], splash_pair['ref'])


def test_get_entropy_similarity(spectrum_pair):
    client.get_entropy_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_weighted_entropy_similarity(spectrum_pair):
    client.get_weighted_entropy_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_total_similarity(spectrum_pair):
    client.get_total_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_cosine_similarity(spectrum_pair):
    client.get_cosine_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_reverse_similarity(spectrum_pair):
    client.get_reverse_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_presence_similarity(spectrum_pair):
    client.get_presence_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_nominal_cosine_similarity(spectrum_pair):
    client.get_nominal_cosine_similarity(spectrum_pair['unk'], spectrum_pair['ref'])


def test_get_composite_similarity(spectrum_pair):
    client.get_composite_similarity(spectrum_pair['unk'], spectrum_pair['ref'])
