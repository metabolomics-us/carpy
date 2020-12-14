from time import time, sleep

import boto3


def test_failed_storage_of_samples_local(stasis_cli, node_evaluator, drop_schema, database):
    purge_queue(stasis_cli)
    # 1. register job description

    log = True
    profiles = ['awstest', 'splashone', 'carrot.lcms.instrument.qtof']

    test_id = "test_job_744_few_samples"

    job = {
        "id": test_id,
        "method": "soqtof[M-H] | 6530a | c18 | negative",
        "samples": [
            "SOP_Plasma_PoolMSMS_003_MX524916_negCSH_800_880",
            "PlasmaMtdBlank001_MX524916_negCSH_preSOP001",
            "PlasmaBiorec002_MX524916_negCSH_postSOP010",
            "SOP002_MX524916_negCSH_Plasma4-QTOF-UC-3",
            "SOP022_MX524916_negCSH_Plasma2-QTOF-UC-1"
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
    # 2. process data locally

    process_run(job, log, node_evaluator, profiles, stasis_cli, test_id)
    # check the state for all samples

    run_steac(log, node_evaluator, profiles, stasis_cli)

    print("reprocessing...")
    process_run(job, log, node_evaluator, profiles, stasis_cli, test_id)
    run_steac(log, node_evaluator, profiles, stasis_cli)
    # evaluate count of data in the database system

    check_sample_count_in_db(database, job, len(job['samples']))
    pass


def run_steac(log, node_evaluator, profiles, stasis_cli):
    print("serving steac")
    purge_queue(stasis_cli)
    # 3. run steac
    stasis_cli.schedule_steac("soqtof[M-H] | 6530a | c18 | negative")
    # 4. reprocess data locally
    node_evaluator.evaluate({
        "single": True,
        "once": True,
        "remove": ['awsdev'],
        "add": profiles,
        "keep": False,
        "log": log
    })


def purge_queue(stasis_cli):
    sqs = boto3.client('sqs')
    queue_url = stasis_cli.schedule_queue()
    assert "test" in queue_url
    # purge the test queue
    sqs.purge_queue(
        QueueUrl=queue_url
    )
    print("wait 60 seconds")
    sleep(60)


def check_spectra_count_in_db(database, job, exspectation):
    pass


def check_target_count_in_db(database, job, exspectation):
    pass


def check_sample_count_in_db(database, job, exspectation):
    samples_with_spectra = "select distinct sample_id from pgspectra p  group by sample_id"
    samples = "select * from pgsample"

    # Query a PostgreSQL table
    cur = database.cursor()
    cur.execute(samples_with_spectra)

    # Retrieve all the rows from the cursor

    rows = cur.fetchall()

    sample_with_spectra_count = 0
    for row in rows:
        sample_with_spectra_count = sample_with_spectra_count + 1

    assert sample_with_spectra_count == exspectation

    cur.execute(samples)

    # Retrieve all the rows from the cursor

    rows = cur.fetchall()

    sample_count = 0
    for row in rows:
        sample_count = sample_count + 1

    assert sample_count == exspectation

    cur.close()


def process_run(job, log, node_evaluator, profiles, stasis_cli, test_id):
    stasis_cli.schedule_job(job_id=test_id)
    sleep(15)
    for sample in job["samples"]:
        node_evaluator.evaluate({
            "single": True,
            "once": True,
            "remove": ['awsdev'],
            "add": profiles,
            "keep": False,
            "log": log
        })
    for sample in job['samples']:
        state = stasis_cli.sample_state(sample, True)
        assert len(state['status']) == 11
    # check the state for all samples
    sleep(15)
    result = stasis_cli.load_job_state(job_id=test_id)
    assert result['job_state'] == 'aggregating_scheduled'
    # there should be one aggregation schedule, process this one
    print("aggregating")
    node_evaluator.evaluate({
        "single": True,
        "once": True,
        "remove": ['awsdev'],
        "add": profiles,
        "keep": False,
        "log": log
    })
    print("Waiting 30s to let triggers catchup")
    sleep(30)
    result = stasis_cli.load_job_state(job_id=test_id)

    assert result['job_state'] == 'aggregated_and_uploaded'
