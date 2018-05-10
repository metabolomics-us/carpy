import simplejson as json

from stasis.route.route import processMetaDataMessage

from stasis.acquisition import get


def test_get(requireMocking):
    # store data

    assert processMetaDataMessage(json.loads(
        "{\"sample\": \"180415dZKsa20_1\", \"acquisition\": {\"instrument\": \"Leco GC-Tof\", \"name\": \"GCTOF\", "
        "\"ionisation\": \"positive\", \"method\": \"gcms\"}, \"metadata\": {\"class\": \"382172\", \"species\": "
        "\"rat\", \"organ\": \"tissue\"}, \"userdata\": {\"label\": \"GP_S_6_006\", \"comment\": \"\"}, "
        "\"time\": 1525121375499, \"id\": \"180415dZKsa20_1\"}"))
    # process data

    result = get.get({
        "pathParameters": {
            "sample": "180415dZKsa20_1"
        }
    }, {})

    print(result)
    assert result['statusCode'] == 200
    assert 'body' in result
    assert json.loads(result['body'])["id"] == "180415dZKsa20_1"
    assert json.loads(result['body'])["acquisition"]["instrument"] == "Leco GC-Tof"
