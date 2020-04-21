from stasis.service.Status import AGGREGATED_AND_UPLOADED, EXPORTED
from stasis.tables import update_job_state, save_sample_state, get_file_by_handle, load_jobs_for_sample


def bucket_json(event, context):
    """
    handles json trigger events
    :param event:
    :param context:
    :return:
    """

    for record in event['Records']:
        o = record['s3']['object']
        k = str(o['key'])

        print("received key {}".format(k))
        sample = get_file_by_handle(k)
        result = save_sample_state(sample=sample, state=EXPORTED, fileHandle=k)

        if result is None:
            print("we were not able to update the sample: {}".format(sample))
        else:
            print("sample state was set to: {}".format(result))
            jobs = load_jobs_for_sample(sample)

            if jobs is not None:
                print("wound {} associated jobs for this sample".format(len(jobs)))
                for job in jobs:
                    from stasis.jobs.sync import sync_job
                    sync_job(job=job)
            else:
                print("we did not find a job for this sample!")


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

            result = update_job_state(job=job, state=AGGREGATED_AND_UPLOADED, reason=f"client uploaded file {k}")

            if result is None:
                print("we were not able to update the job")
            else:
                print("job state was set to: {}".format(result))

        else:
            print("received wrong key type, ignored!")
