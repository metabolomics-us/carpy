from time import time, sleep

import boto3


def test_failed_storage_of_samples_local(stasis_cli, node_evaluator):
    sqs = boto3.client('sqs')

    queue_url = stasis_cli.schedule_queue()

    assert "test" in queue_url
    print("purging the queue")
    # purge the test queue
    sqs.purge_queue(
        QueueUrl=queue_url
    )

    print("wait 60 seconds")
    sleep(60)
    # 1. register job description

    test_id = "test_job_744_few_samples"

    job = {
        "id": test_id,
        "method": "soqtof[M-H] | 6530a | c18 | negative",
        "samples": [
            "SOP_Plasma_PoolMSMS_003_MX524916_negCSH_800_880.mzml",
            "PlasmaMtdBlank001_MX524916_negCSH_preSOP001.mzml",
            "PlasmaBiorec002_MX524916_negCSH_postSOP010.mzml",
            "SOP002_MX524916_negCSH_Plasma4-QTOF-UC-3.mzml",
            "SOP022_MX524916_negCSH_Plasma2-QTOF-UC-1.mzml"
        ],
        "profile": "carrot.lcms",

        "meta": {
            "tracking": [
                {
                    "state": "entered",
                },
                {
                    "state": "acquired",
                    "extension": "d"
                },
                {
                    "state": "converted",
                    "extension": "mzml"
                },
            ]
        }

    }

    stasis_cli.store_job(job=job.copy())
    stasis_cli.schedule_job(job_id=test_id)
    # 2. process data locally

#    for sample in job["samples"]:
#        node_evaluator.evaluate({
#            "single": True,
#            "once": True,
#            "remove": ['awsdev'],
#            "add": ['awstest', 'splashone'],
#            "keep": False,
#            "log": False
#        })
#
#    # there should be one aggregation schedule, process this one
#    node_evaluator.evaluate({
#        "single": True,
#        "once": True,
#        "remove": ['awsdev'],
#        "add": ['awstest', 'splashone'],
#        "keep": False,
#        "log": False
#    })

    # 3. run steac
    stasis_cli.schedule_steac("soqtof[M-H] | 6530a | c18 | negative")

    # 4. reprocess data locally

    # 5. validate data in data

    pass
