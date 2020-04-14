from stasis.service.Status import AGGREGATED
from stasis.tables import update_job_state


def bucket_zip(event, context):
    """
    triggers the job api on uploaded files
    :param event:
    :param context:
    :return:
    """

    print("received upload request")
    for record in event['Records']:
        o = record['s3']['object']
        k = str(o['key'])

        print("received key {}".format(k))
        if k.endswith(".zip"):
            job = k.replace(".zip", "")
            print(f"belongs to job {job}")

            result = update_job_state(job=job, state=AGGREGATED, reason=f"client uploaded file {k}")

            if result is None:
                print("we were not able to update the job")
            else:
                print("job state was set to: {}".format(result))

        else:
            print("received wrong key type, ignored!")
