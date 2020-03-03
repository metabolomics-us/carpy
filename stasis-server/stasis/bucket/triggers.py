from stasis.jobs.states import States
from stasis.tables import update_job_state, update_sample_state


def bucket_zip(event, context):
    """
    triggers the job api on uploaded files
    :param event:
    :param context:
    :return:
    """

    for record in event['Records']:
        o = record['s3']['object']
        k = str(o['key'])

        if k.endswith(".zip"):
            job = k.replace(".zip", "")

            result = update_job_state(job=job, state=States.AGGREGATED, reason="client uploaded file")

            if result is None:
                print("we were not able to update the job")
            else:
                print("job state was set to: {}".format(result))


def bucket_json(event, context):
    """
    whenever a while is uploaded, all jobs having this sample will be updated with the information
    that this sample finished processing.
    :param event:
    :param context:
    :return:
    """

    for record in event['Records']:
        o = record['s3']['object']
        k = str(o['key'])

        if k.endswith(".json"):
            sample = k.replace(".json", "")

            result = update_sample_state(sample=sample, state=States.PROCESSED,
                                         reason="processed file uploaded to the related bucket")

            if result is None:
                print("we were not able to update the job")
            else:
                print("the following jobs were updated: {}".format(result))
