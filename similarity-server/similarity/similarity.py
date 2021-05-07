from abc import ABC
from pprint import pprint
from urllib import parse

import simplejson as json
import spectral_similarity

from similarity import headers


class SimilarityResult(ABC):
    def __init__(self, algorithm, value, remove_prec):
        self.algorithm = algorithm
        self.similarity = value,
        self.removePrecursor = remove_prec

    def default(self, o):
        return o.__dict__


def missing_param(msg: str):
    return {
        "statusCode": 400,
        "headers": headers.__HTTP_HEADERS__,
        "body": {
            "error": msg
        }
    }


def bad_path():
    return {
        "statusCode": 400,
        "headers": headers.__HTTP_HEADERS__,
        "body": ""
    }


def make_array(spectrum: str):
    peaks = spectrum.split(" ")
    arr = [p.split(":") for p in peaks]
    pprint(arr)
    return arr


def list_algorithms():
    return {
        "statusCode": 200,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps(spectral_similarity.methods_name)
    }


def all_similarities(event, context):
    if 'queryStringParameters' in event:
        if 'unknown' not in event['queryStringParameters']:
            return missing_param("Missing unknown spectrum")
        if 'reference' not in event['queryStringParameters']:
            return missing_param("Missing reference spectrum")
    else:
        return bad_path()

    unknown = make_array(parse.unquote(event['queryStringParameters']['unknown']))
    reference = make_array(parse.unquote(event['queryStringParameters']['reference']))

    try:
        results = [{"algorithm": spectral_similarity.methods_name[algo], "similarity": spectral_similarity.similarity(
            spectrum_query=unknown, spectrum_library=reference, method=algo, ms2_da=0.005
        ), "removePrecursor": False} for algo in spectral_similarity.methods_name.keys()]

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps(results, use_decimal=True)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({"error": str(e)}, use_decimal=True)
        }


def similarity(event, context):
    if 'queryStringParameters' in event:
        if 'unknown' not in event['queryStringParameters']:
            return missing_param("Missing unknown spectrum")
        if 'reference' not in event['queryStringParameters']:
            return missing_param("Missing reference spectrum")
    else:
        return bad_path()

    if 'pathParameters' in event:
        if 'algo' not in event['pathParameters']:
            return missing_param("Missing algorithm")
    else:
        return bad_path()

    try:
        unknown = make_array(parse.unquote(event['queryStringParameters']['unknown']))
        reference = make_array(parse.unquote(event['queryStringParameters']['reference']))
        algo = parse.unquote(event['pathParameters']['algorithm'])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({"algorithm": spectral_similarity.methods_name[algo], "similarity": spectral_similarity.similarity(
                spectrum_query=unknown, spectrum_library=reference, method=algo, ms2_da=0.005
            ), "removePrecursor": False}, use_decimal=True)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({"error": str(e)}, use_decimal=True)
        }
