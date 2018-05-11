import simplejson as json
import time
import requests
import logging

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

from stasis.acquisition import create


apiUrl = "https://test-api.metabolomics.us/stasis/acquisition"
samplename = f'test_{time.time()}'

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def test_create():
    data = {
        'sample': samplename,
        'acquisition': {
            'instrument': 'test inst',
            'name': 'method blah',
            'ionisation': 'positive',  # psotivie || negative
            'method': 'gcms'  # gcms || lcms
        },
        'metadata': {
            'class': '12345',
            'species': 'alien',
            'organ': 'honker'
        },
        'userdata': {
            'label': 'filexxx',
            'comment': '',
        },
    }

    response = requests.post(apiUrl, json=data)

    assert 200 == response.status_code

    time.sleep(5)

    response = requests.get(apiUrl + '/' + samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']
