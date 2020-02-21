from stasis.jobs.states import States
from stasis.tables import update_job_state


def bucket_zip(event, context):
    """
    triggers the job api on uploaded files
    :param event:
    :param context:
    :return:
    """

    print("new file uploaded....")
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
