import os

from stasis.service.Bucket import Bucket


def test_bucket_operations_txt(requireMocking):
    """
        simple test for out bucket
    :param requireMocking:
    :return:
    """

    bucket = Bucket(os.environ["resultTable"])
    assert not bucket.exists("test.txt")

    bucket.save("test.txt", "tada")

    assert bucket.exists("test.txt")

    assert bucket.load("test.txt") == "tada"

    bucket.delete("test.txt")

    assert not bucket.exists("test.txt")


def test_bucket_operations_bin(requireMocking):
    """
        simple test for out bucket
    :param requireMocking:
    :return:
    """

    bucket = Bucket(os.environ["resultTable"])
    assert not bucket.exists("test.zip")

    bucket.save("test.zip", str.encode("tada"))

    assert bucket.exists("test.zip")

    assert bucket.load("test.zip",binary=True) == str.encode("tada")

    bucket.delete("test.zip")

    assert not bucket.exists("test.zip")
