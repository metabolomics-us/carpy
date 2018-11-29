import boto3
import simplejson as json
from boltons.iterutils import remap


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
        self.drop_falsey = lambda path, key, value: True if isinstance(value, (int, float, complex)) else bool(value)

    def load(self, sample):
        """
            loads a given object from the database storage
        :param sample:
        :return:
        """

        result = self.table.get_item(
            Key={
                'id': sample
            }
        )

        if 'Item' in result:
            return result['Item']
        else:
            print(result)
            return None

    def save(self, object):
        """

        saves and object to the database storage with the specific key

        :param object:
        :return:
        """

        # force serialization to deal with decimal number tag
        data = remap(object, visit=self.drop_falsey)
        data = json.dumps(data, use_decimal=True)
        data = json.loads(data, use_decimal=True)
        print(data)
        return self.table.put_item(Item=data)

    def delete(self, sample):
        """
        deletes and object from the database storage with the specific key

        :param object:
        :return:
        """

        table = self.db.Table(self.table)
        # quering to get pk

        print("deleting tracking of sample '%s'" % sample)
        result = table.delete_item(Key={'id': sample, 'sample': sample})

        return result
