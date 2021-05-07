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


def server_error(msg: str):
    return {
        "statusCode": 500,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({"error": msg})
    }


def success(data, use_decimal: bool = False):
    return {
        "statusCode": 200,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps(data, use_decimal=use_decimal)
    }


def make_array(spectrum: str):
    peaks = spectrum.split(" ")
    arr = [p.split(":") for p in peaks]
    pprint(arr)
    return arr


def list_algorithms():
    algorithms = [{"name": k, "description": v} for k, v in spectral_similarity.methods_name.items()]

    return success(algorithms)


def all_similarities(event, context):
    remove_precursor = False
    ms2_tolerance = 0.005

    if 'queryStringParameters' in event:
        if 'unknown' not in event['queryStringParameters']:
            return missing_param("Missing unknown spectrum")
        if 'reference' not in event['queryStringParameters']:
            return missing_param("Missing reference spectrum")
        if 'removePrecursor' in event['queryStringParameters']:
            remove_precursor = event['queryStringParameters']['removePrecursor']
        if 'ms2_tolerance' in event['queryStringParameters']:
            ms2_tolerance = event['queryStringParameters']['ms2_tolerance']
    else:
        return bad_path()

    unknown = make_array(parse.unquote(event['queryStringParameters']['unknown']))
    reference = make_array(parse.unquote(event['queryStringParameters']['reference']))

    try:
        results = [{"algorithm": spectral_similarity.methods_name[algo], "similarity": spectral_similarity.similarity(
            spectrum_query=unknown, spectrum_library=reference, method=algo, ms2_da=ms2_tolerance
        ), "removePrecursor": remove_precursor} for algo in spectral_similarity.methods_name.keys()]

        return success(results, use_decimal=True)

    except Exception as e:
        return server_error(str(e))


def similarity(event, context):
    remove_precursor = False
    ms2_tolerance = 0.005

    if 'queryStringParameters' in event:
        if 'unknown' not in event['queryStringParameters']:
            return missing_param("Missing unknown spectrum")
        if 'reference' not in event['queryStringParameters']:
            return missing_param("Missing reference spectrum")
        if 'removePrecursor' in event['queryStringParameters']:
            remove_precursor = event['queryStringParameters']['removePrecursor']
        if 'ms2_tolerance' in event['queryStringParameters']:
            ms2_tolerance = event['queryStringParameters']['ms2_tolerance']
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

        data = {"algorithm": spectral_similarity.methods_name[algo], "similarity": spectral_similarity.similarity(
                    spectrum_query=unknown, spectrum_library=reference, method=algo, ms2_da=ms2_tolerance
                ), "removePrecursor": remove_precursor}

        return success(data, use_decimal=True)
    except Exception as e:
        msg = str(e)
        return server_error(msg)
