from time import sleep

import boto3


def test_schedule_steac(stasis_cli, node_evaluator, drop_schema):
    sqs = boto3.client('sqs')

    queue_url = stasis_cli.schedule_queue()

    assert "test" in queue_url
    # purge the test queue
    sqs.purge_queue(
        QueueUrl=queue_url
    )

    print("wait 60 seconds")
    sleep(60)
    # 1. register job description

    test_id = "test_job_676"

    job = {
        "id": test_id,
        "method": "soqtof[M-H] | 6530a | c18 | negative",
        "samples": [
            "SOP_Plasma_PoolMSMS_003_MX524916_negCSH_800_880.mzml",
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

    for sample in job["samples"]:
        node_evaluator.evaluate({
            "single": True,
            "once": True,
            "remove": ['awsdev'],
            "add": ['awstest', 'splashone'],
            "keep": False,
            "log": False
        })

    # there should be one aggregation schedule, process this one
    node_evaluator.evaluate({
        "single": True,
        "once": True,
        "remove": ['awsdev'],
        "add": ['awstest', 'splashone'],
        "keep": False,
        "log": False
    })

    # 3. run steac
    stasis_cli.schedule_steac("soqtof[M-H] | 6530a | c18 | negative")

    # 4. reprocess data locally
    node_evaluator.evaluate({
        "single": True,
        "once": True,
        "remove": ['awsdev'],
        "add": ['awstest', 'splashone'],
        "keep": False,
        "log": False
    })

    pass
