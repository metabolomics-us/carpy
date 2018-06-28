import time
import simplejson as json
from stasis.schedule import schedule as s


def test_schedule(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'env': 'test', 'method': 'hello', 'mode': 'lcms'})

    response = s.schedule({'body': jsonString}, {})
