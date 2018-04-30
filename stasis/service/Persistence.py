import boto3


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

        print(result)
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
        return table.put_item(Item=object)
