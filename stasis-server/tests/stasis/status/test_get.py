import simplejson as json

from stasis.service.Status import *
from stasis.status import get


def test_get_status_map(requireMocking):
    states = {ENTERED: 1,
              ACQUIRED: 100,
              CONVERTED: 200,
              SCHEDULING: 299,
              SCHEDULED: 300,
              PROCESSING: 400,
              DECONVOLUTED: 410,
              CORRECTED: 420,
              ANNOTATED: 430,
              QUANTIFIED: 440,
              REPLACED: 450,
              EXPORTED: 500,
              AGGREGATING_SCHEDULING: 548,
              AGGREGATING_SCHEDULED: 549,
              AGGREGATING: 550,
              AGGREGATED: 590,
              AGGREGATED_AND_UPLOADED: 591,
              FINISHED: 600,
              FAILED: 900
              }
    result = get.get({}, {})

    status = json.loads(result['body'])

    assert status == states
