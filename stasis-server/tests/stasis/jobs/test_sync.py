import json

from stasis.jobs import tracking
from stasis.jobs.schedule import store_job
from stasis.jobs.sync import update_job_state, EXPORTED, FAILED, calculate_job_state
from stasis.schedule.backend import Backend
from stasis.service.Status import SCHEDULED, REPLACED
from stasis.tables import TableManager, load_job_samples_with_states, set_sample_job_state


def test_sync_processed(requireMocking, mocked_10_sample_job):
    tm = TableManager()

    for i in range(0, 10):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

        assert load_job_samples_with_states("12345")['abc_{}'.format(i)] == "scheduled"
        # dummy stasis data which need to be in the system for this test to pass
        tm.get_tracking_table().put_item(Item=
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

    calculate_job_state(job="12345")

    samples = load_job_samples_with_states("12345")
    assert all(value == str(EXPORTED) for value in samples.values())


def test_sync_currently_processing(requireMocking, mocked_10_sample_job):
    tm = TableManager()

    for i in range(0, 10):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": SCHEDULED
            }
        )}, {})

        assert load_job_samples_with_states("12345")['abc_{}'.format(i)] == "scheduled"
        # dummy stasis data which need to be in the system for this test to pass
        tm.get_tracking_table().put_item(Item=
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

    calculate_job_state(job="12345")

    assert all(value == str(REPLACED) for value in load_job_samples_with_states("12345").values())


def test_job_is_in_state_processing(requireMocking, mocked_10_sample_job):
    for i in range(0, 10):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

    assert load_job_samples_with_states("12345")['abc_{}'.format(i)] == "scheduled"
    # dummy stasis data which need to be in the system for this test to pass

    new_states = [
        {
            "sample": "abc_{}".format(0),
            "fileHandle": "abc_{}.d".format(0),
            "priority": 1,
            "time": 1563307359163,
            "value": "entered"
        },
        {
            "sample": "abc_{}".format(1),
            "fileHandle": "abc_{}.d".format(1),
            "priority": 100,
            "time": 1563307360393,
            "value": "acquired"
        },
        {
            "sample": "abc_{}".format(2),
            "fileHandle": "abc_{}.mzml".format(2),
            "priority": 200,
            "time": 1563307361543,
            "value": "converted"
        },
        {
            "sample": "abc_{}".format(3),
            "fileHandle": "abc_{}.mzml".format(3),
            "priority": 300,
            "time": 1563330092360,
            "value": "scheduled"
        },
        {
            "sample": "abc_{}".format(4),
            "fileHandle": "abc_{}.mzml".format(4),
            "priority": 410,
            "time": 1563330183632,
            "value": "deconvoluted"
        },
        {
            "sample": "abc_{}".format(5),
            "fileHandle": "abc_{}.mzml".format(5),
            "priority": 420,
            "time": 1563330184868,
            "value": "corrected"
        },
        {
            "sample": "abc_{}".format(6),
            "fileHandle": "abc_{}.mzml".format(6),
            "priority": 430,
            "time": 1563330189108,
            "value": "annotated"
        },
        {
            "sample": "abc_{}".format(7),
            "fileHandle": "abc_{}.mzml".format(7),
            "priority": 440,
            "time": 1563330190650,
            "value": "quantified"
        },
        {
            "sample": "abc_{}".format(8),
            "fileHandle": "abc_{}.mzml".format(8),
            "priority": 900,
            "time": 1563330244348,
            "value": "failed"
        }
    ]

    for x in new_states:
        set_sample_job_state(
            sample=x['sample'],
            job="12345",
            state=x['value'],
            reason="it's a test"

        )
    state = calculate_job_state(job="12345")

    assert state == 'processing'


def test_job_is_in_state_exported(requireMocking, mocked_10_sample_job):
    for i in range(0, 10):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

    assert load_job_samples_with_states("12345")['abc_{}'.format(i)] == "scheduled"
    # dummy stasis data which need to be in the system for this test to pass

    new_states = [
        {
            "sample": "abc_{}".format(0),
            "fileHandle": "abc_{}.d".format(0),
            "priority": 1,
            "time": 1563307359163,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(1),
            "fileHandle": "abc_{}.d".format(1),
            "priority": 100,
            "time": 1563307360393,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(2),
            "fileHandle": "abc_{}.mzml".format(2),
            "priority": 200,
            "time": 1563307361543,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(3),
            "fileHandle": "abc_{}.mzml".format(3),
            "priority": 300,
            "time": 1563330092360,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(4),
            "fileHandle": "abc_{}.mzml".format(4),
            "priority": 410,
            "time": 1563330183632,
            "value": "exported"
        },
        {
            "sample": "abc_{}".format(5),
            "fileHandle": "abc_{}.mzml".format(5),
            "priority": 420,
            "time": 1563330184868,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(6),
            "fileHandle": "abc_{}.mzml".format(6),
            "priority": 430,
            "time": 1563330189108,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(7),
            "fileHandle": "abc_{}.mzml".format(7),
            "priority": 440,
            "time": 1563330190650,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(8),
            "fileHandle": "abc_{}.mzml".format(8),
            "priority": 900,
            "time": 1563330244348,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(9),
            "fileHandle": "abc_{}.mzml".format(8),
            "priority": 900,
            "time": 1563330244348,
            "value": EXPORTED
        }

    ]

    for x in new_states:
        set_sample_job_state(
            sample=x['sample'],
            job="12345",
            state=x['value'],
            reason="it's a test"

        )
    state = calculate_job_state(job="12345")

    assert state == EXPORTED

def test_job_is_in_state_exported_even_with_a_failed_sample(requireMocking, mocked_10_sample_job):
    for i in range(0, 10):
        tracking.create({'body': json.dumps(
            {
                "job": "12345",
                "sample": "abc_{}".format(i),
                "state": "scheduled"
            }
        )}, {})

    assert load_job_samples_with_states("12345")['abc_{}'.format(i)] == "scheduled"
    # dummy stasis data which need to be in the system for this test to pass

    new_states = [
        {
            "sample": "abc_{}".format(0),
            "fileHandle": "abc_{}.d".format(0),
            "priority": 1,
            "time": 1563307359163,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(1),
            "fileHandle": "abc_{}.d".format(1),
            "priority": 100,
            "time": 1563307360393,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(2),
            "fileHandle": "abc_{}.mzml".format(2),
            "priority": 200,
            "time": 1563307361543,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(3),
            "fileHandle": "abc_{}.mzml".format(3),
            "priority": 300,
            "time": 1563330092360,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(4),
            "fileHandle": "abc_{}.mzml".format(4),
            "priority": 410,
            "time": 1563330183632,
            "value": "exported"
        },
        {
            "sample": "abc_{}".format(5),
            "fileHandle": "abc_{}.mzml".format(5),
            "priority": 420,
            "time": 1563330184868,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(6),
            "fileHandle": "abc_{}.mzml".format(6),
            "priority": 430,
            "time": 1563330189108,
            "value": FAILED
        },
        {
            "sample": "abc_{}".format(7),
            "fileHandle": "abc_{}.mzml".format(7),
            "priority": 440,
            "time": 1563330190650,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(8),
            "fileHandle": "abc_{}.mzml".format(8),
            "priority": 900,
            "time": 1563330244348,
            "value": EXPORTED
        },
        {
            "sample": "abc_{}".format(9),
            "fileHandle": "abc_{}.mzml".format(8),
            "priority": 900,
            "time": 1563330244348,
            "value": EXPORTED
        }

    ]

    for x in new_states:
        set_sample_job_state(
            sample=x['sample'],
            job="12345",
            state=x['value'],
            reason="it's a test"

        )
    state = calculate_job_state(job="12345")

    assert state == EXPORTED
