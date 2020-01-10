import json

from jobs import tracking
from jobs.stasis import sync
from jobs.states import States
from jobs.table import TableManager, load_job


def test_sync_processed(requireMocking):
    tm = TableManager()

    for i in range(0, 100):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

        assert load_job("12345")['abc_{}'.format(i)] == "scheduled"
        # dummy stasis data which need to be in the system for this test to pass
        tm.get_stasis_tracking_table().put_item(Item=
        {
            "experiment": "12345",
            "id": "abc_{}".format(i),
            "sample": "abc_{}".format(i),
            "status": [
                {
                    "fileHandle": "abc_{}.d".format(i),
                    "priority": 1,
                    "time": 1563307359163,
                    "value": "entered"
                },
                {
                    "fileHandle": "abc_{}.d".format(i),
                    "priority": 100,
                    "time": 1563307360393,
                    "value": "acquired"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 200,
                    "time": 1563307361543,
                    "value": "converted"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 300,
                    "time": 1563330092360,
                    "value": "scheduled"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 410,
                    "time": 1563330183632,
                    "value": "deconvoluted"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 420,
                    "time": 1563330184868,
                    "value": "corrected"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 430,
                    "time": 1563330189108,
                    "value": "annotated"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 440,
                    "time": 1563330190650,
                    "value": "quantified"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 450,
                    "time": 1563330244348,
                    "value": "replaced"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 500,
                    "time": 1563330249927,
                    "value": "exported"
                }
            ]
        }
        )

    sync(job="12345")

    assert all(value == str(States.PROCESSED) for value in load_job("12345").values())


def test_sync_currently_processing(requireMocking):
    tm = TableManager()

    for i in range(0, 100):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

        assert load_job("12345")['abc_{}'.format(i)] == "scheduled"
        # dummy stasis data which need to be in the system for this test to pass
        tm.get_stasis_tracking_table().put_item(Item=
        {
            "experiment": "12345",
            "id": "abc_{}".format(i),
            "sample": "abc_{}".format(i),
            "status": [
                {
                    "fileHandle": "abc_{}.d".format(i),
                    "priority": 1,
                    "time": 1563307359163,
                    "value": "entered"
                },
                {
                    "fileHandle": "abc_{}.d".format(i),
                    "priority": 100,
                    "time": 1563307360393,
                    "value": "acquired"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 200,
                    "time": 1563307361543,
                    "value": "converted"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 300,
                    "time": 1563330092360,
                    "value": "scheduled"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 410,
                    "time": 1563330183632,
                    "value": "deconvoluted"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 420,
                    "time": 1563330184868,
                    "value": "corrected"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 430,
                    "time": 1563330189108,
                    "value": "annotated"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 440,
                    "time": 1563330190650,
                    "value": "quantified"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 450,
                    "time": 1563330244348,
                    "value": "replaced"
                }
            ]
        }
        )

    sync(job="12345")

    assert all(value == str(States.PROCESSING) for value in load_job("12345").values())


def test_sync_failed(requireMocking):
    tm = TableManager()

    for i in range(0, 100):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

        assert load_job("12345")['abc_{}'.format(i)] == "scheduled"
        # dummy stasis data which need to be in the system for this test to pass
        tm.get_stasis_tracking_table().put_item(Item=
        {
            "experiment": "12345",
            "id": "abc_{}".format(i),
            "sample": "abc_{}".format(i),
            "status": [
                {
                    "fileHandle": "abc_{}.d".format(i),
                    "priority": 1,
                    "time": 1563307359163,
                    "value": "entered"
                },
                {
                    "fileHandle": "abc_{}.d".format(i),
                    "priority": 100,
                    "time": 1563307360393,
                    "value": "acquired"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 200,
                    "time": 1563307361543,
                    "value": "converted"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 300,
                    "time": 1563330092360,
                    "value": "scheduled"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 410,
                    "time": 1563330183632,
                    "value": "deconvoluted"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 420,
                    "time": 1563330184868,
                    "value": "corrected"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 430,
                    "time": 1563330189108,
                    "value": "annotated"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 440,
                    "time": 1563330190650,
                    "value": "quantified"
                },
                {
                    "fileHandle": "abc_{}.mzml".format(i),
                    "priority": 900,
                    "time": 1563330244348,
                    "value": "failed"
                }
            ]
        }
        )

    sync(job="12345")

    assert all(value == str(States.FAILED) for value in load_job("12345").values())
