import boto3


class Bucket:
    """
        this defines an easy access to a AWS bucket
    """

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource('s3')

        try:
            boto3.client('s3').create_bucket(Bucket=bucket_name)
        except botocore.errorfactory.BucketAlreadyExists as e:
            print("sorry this bucket BucketAlreadyExists")

    def save(self, name, content):
        """
        stores the specified content in the bucket
        :param name: the name of the content
        :param content: the content
        :return:
        """
        return self.s3.Object(self.bucket_name, name).put(Body=content)

    def load(self, name):
        """
            loads the specified content
        :param name: the name of the content
        :return:
        """
        try:
            print("loading: {}".format(name))
            data = self.s3.Object(self.bucket_name, name).get()['Body']

            return data.read().decode()
        except Exception as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def exists(self, name) -> bool:
        """
        checks if the content with the given name exists
        :param name:
        :return:
        """

        try:
            self.s3.Object(self.bucket_name, name).load()
            return True
        except Exception as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                return False
            else:
                # Something else has gone wrong.
                raise

    def delete(self, name):
        """
            deletes the given data entry
        :param name:
        :return:
        """
        self.s3.Object(self.bucket_name, name).delete()
