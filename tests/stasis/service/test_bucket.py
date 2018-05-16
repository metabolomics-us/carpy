from stasis.service.Bucket import Bucket


def test_bucket_operations(requireMocking):
    """
        simple test for out bucket
    :param requireMocking:
    :return:
    """

    bucket = Bucket("test_bucket")
    assert not bucket.exists("test.txt")

    bucket.save("test.txt", "tada")

    assert bucket.exists("test.txt")

    assert bucket.load("test.txt") == "tada"

    bucket.delete("test.txt")

    assert not bucket.exists("test.txt")
