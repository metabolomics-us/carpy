import requests
from http.client import HTTPConnection

class DataformerClient(object):
    """Simple DataFormer rest api client

    Attributes:
        dataform_url    The DataFormer API's base URL
        storage         The destination folder for dwonloaded files
    """

    HTTPConnection.debugLevel=1

    dataformer_url = ""
    dataformer_port = ""
    storage = ""

    def __init__(self, api_url, api_port, storage):
        self.dataformer_url = f"{api_url}:{api_port}"
        self.storage = storage

    def convert(self, file, type):
        """Converts a file to specified type

        Parameters
        ----------
            file : str
                The name of the file to download
            type : str
                The converted type, valid values are: 'mzml' or 'mzxml'
        """
        print(" convert %s to %s" % (file, type))

        try:
            if(self.__private_upload(file)):
                d = self.__private_download(file, type)
                print("donloaded %s" % d)
                return d
            else:
                return ""
        except Exception as ex:
            print("ERROR: " + str(ex.args))
            return ""


    def __private_upload(self, file):
        """Uploads a file to be converted

        Parameters
        ----------
            file : str
                The raw data file to be uploaded and converted (the conversion happens automatically)
        """
        print("...upoloading %s" % file)
        headers = {'Content-type': 'multipart/form-data'}

        files = {"file": open(file, "rb")}
        uploaded = requests.post(f"{self.dataformer_url}/rest/conversion/upload", files=files, headers=headers)
        if uploaded.status_code == 200:
            print("\tuploaded")
            return True
        else:
            print("\terror uploading\n%d - %s" % (uploaded.status_code, uploaded.reason))
            return False

    def __private_download(self, file, type):
        """Download a converted file of a particular type

        Parameters
        ----------
            file : str
                The name of the file to download
            type : str
                The converted type, valid values are: 'mzml' or 'mzxml'
        """
        if(type not in ['mzml', 'mzxml']):
            raise Exception("Unsupported file type, please use 'mzml' or 'mzxml'")

        print("...download %s version of %s" % (type, file))

        # data = requests.get(f"{self.dataformer_url}/rest/conversion/download/{type}")
        download = f"{file}.{type}"
        # open(download, "wb").write(data.content)
        return download
