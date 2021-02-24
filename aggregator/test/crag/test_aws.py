from time import time

from crag.aws import JobAggregator


def test_aggregate_success(api_token, stasis):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "soqtof[M+H][M+NH4] | 6530a | c18 | positive",
        "samples": [
            "SOP_Plasma_PoolMSMS_001_MX524916_negCSH_60_700",
            "SOP_Plasma_PoolMSMS_002_MX524916_negCSH_700_800",
            "SOP_Plasma_PoolMSMS_003_MX524916_negCSH_800_880"
        ],
        "profile": "carrot.lcms",
    }

    stasis.store_job(job=job)

    aggregate = JobAggregator({}, stasis)

    assert aggregate.aggregate_job(test_id, upload=True) is True


def test_aggregate_false(api_token, stasis):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "samples": [
            "B2a_TEDDYLiNO_EXISTpids_Neg_NIST001",
            "B10A_SA8931_TeddyNO_EXISTLipids_Pos_14TCZ",
            "B10A_SA8922_TeddyFAILEDLipids_Pos_122WP"
        ],
        "profile": "carrot.lcms",
    }

    stasis.store_job(job=job)

    aggregate = JobAggregator({}, stasis)

    assert aggregate.aggregate_job(test_id, upload=True) is False
