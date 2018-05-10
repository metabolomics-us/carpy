import boto3
import simplejson as json


class Persistence:
    """
        simplistic persistence framework
    """

    def __init__(self, table):
        """
            creates a new object with the associated table
        :param table:
        """

        self.table = table
        self.db = boto3.resource('dynamodb')

    def load(self, sample):
        """
            loads a given object from the database storage
        :param sample:
        :return:
        """

        table = self.db.Table(self.table)
        result = table.get_item(
            Key={
                'id': sample
            }
        )

        if 'Item' in result:
            return result['Item']
        else:
            return None

    def save(self, object):
        """

        saves and object to the database storage with the specific key

        :param object:
        :return:
        """

        table = self.db.Table(self.table)

        # force serialization to deal with decimal number tag
        data = json.dumps(object, use_decimal=True)
        data = json.loads(data, use_decimal=True)
        print(data)
        return table.put_item(Item=data)
