import os
import requests
from http.client import HTTPConnection

class StasisClient(object):
    """Simple Stasis rest api client"""

    HTTPConnection.debugLevel=1

    stasis_url = ""

    def __init__(self, api_url):
        self.stasis_url = api_url

    def set_tracking(self, sample, status):
        """Creates a new status or changes the status of a sample

        Parameters
        ----------
            sample : str
                The filename of the sample to create/adjust tracking status
            status : str
                The new status of a file. Can be one of: 'entered', 'acquired', 'converted', 'processed', 'exported'
        """
        if(status not in ['entered', 'acquired', 'converted', 'processed', 'exported']):
            return False

        print("...setting tracking for sample %s to %s ..." % (sample, status))

        filename, ext = os.path.splitext(sample)
        resp = requests.post(self.stasis_url + "/stasis/tracking", data={sample:filename, status:status})

        if(resp.status_code == 200):
            print("\tsuccess")
        else:
            print("\tfail\n%d - %s" % (resp.status_code, resp.reason))

        return resp.status_code == 200
