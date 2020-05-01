import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.headers import __HTTP_HEADERS__
from stasis.jobs.sync import update_job_state, EXPORTED, FAILED, AGGREGATED, calculate_job_state
from stasis.tables import TableManager, _set_sample_job_state, load_job_samples


def create(event, context):
    """
    creates a new tracking record in the dynamodb database
    """
    assert 'body' in event
    body: dict = json.loads(event['body'])

    return _set_sample_job_state(body)


def get(event, context):
    """
    gets the information for the specific record in the dynamodb database
    """

    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'sample' in parameters and 'job' in parameters:
            tm = TableManager()
            id = tm.generate_job_id(parameters['job'], parameters['sample'])
            table = tm.get_job_sample_state_table()

            result = table.query(
                KeyConditionExpression=Key('id').eq(id)
            )

            if "Items" in result and len(result['Items']) > 0:
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(result['Items'][0])
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no sample found with this identifier : {}".format(
                        event['pathParameters']['sample'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def status(event, context):
    """
    returns the status of the current job, as well as some meta information

    TODO due to expense it might be better to store the whole calculation result
    in an addiitonal table, since it can take a LONG time to execute and so not perfect
    as solution for http requests
    """

    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'job' in parameters:
            job = parameters['job']

            tm = TableManager()
            table_overall_state = tm.get_job_state_table()

            sample_states = load_job_samples(job)

            if sample_states is None:
                sample_states = {}

            job_state = table_overall_state.query(
                **{
                    'IndexName': 'job-id-state-index',
                    'Select': 'ALL_ATTRIBUTES',
                    'KeyConditionExpression': Key('job').eq(job)
                }
            )

            states = {}
            for x in sample_states.values():
                if x not in states:
                    states[x] = 0

                states[x] = states[x] + 1

            # this queries the state of all the samples
            if "Items" in job_state and len(job_state['Items']) > 0:
                job_state = job_state["Items"]

                if len(job_state) > 0:
                    job_state = job_state[0]
                    return {
                        "statusCode": 200,
                        "headers": __HTTP_HEADERS__,
                        "body": json.dumps({
                            "count": len(sample_states),
                            "sample_states": states,
                            "job_state": job_state['state'],
                            "job_info": job_state
                        }
                        )
                    }
                else:
                    return {
                        "statusCode": 503,
                        "headers": __HTTP_HEADERS__,
                        "body": json.dumps({
                            "sample_states": states,
                            "job_state": "no associated state found!",
                        }
                        )
                    }

            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no job found with this identifier : {}".format(
                        event['pathParameters']['job'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def description(event, context):
    """
    returns the complete job description, which can be rather long
    """
    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'job' in parameters:
            job = parameters['job']
            tm = TableManager()
            table = tm.get_job_sample_state_table()

            query_params = {
                'IndexName': 'job-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('job').eq(job)
            }
            result = table.query(**query_params
                                 )

            if "Items" in result and len(result['Items']) > 0:

                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(
                        result['Items']

                    )
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no job found with this identifier : {}".format(
                        event['pathParameters']['job'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def job_can_aggregate(event, context):
    """
    computes if the given job can be aggregated. Basically the status of all items of the job has to be failed or processed
    for this to be possible
    """
    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'job' in parameters:
            job = parameters['job']
            tm = TableManager()
            table = tm.get_job_sample_state_table()

            query_params = {
                'IndexName': 'job-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('job').eq(job)
            }
            result = table.query(**query_params
                                 )

            if "Items" in result and len(result['Items']) > 0:

                for item in result['Items']:
                    if item['state'] not in [EXPORTED, FAILED]:
                        return {
                            "statusCode": 200,
                            "headers": __HTTP_HEADERS__,
                            "body": json.dumps(
                                {'can_aggregate': False}
                            )
                        }

                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(
                        {'can_aggregate': True}
                    )
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no job found with this identifier : {}".format(
                        event['pathParameters']['job'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def job_is_done(event, context):
    """
    computes if the given job is done, meaning aggregation is completed and result can be downloaded. The states for all samples has to be
    be failed or aggregated
    """
    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'job' in parameters:
            job = parameters['job']
            tm = TableManager()
            table = tm.get_job_sample_state_table()

            query_params = {
                'IndexName': 'job-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('job').eq(job)
            }
            result = table.query(**query_params
                                 )

            if "Items" in result and len(result['Items']) > 0:

                for item in result['Items']:
                    if item['state'] not in [AGGREGATED, FAILED]:
                        return {
                            "statusCode": 200,
                            "headers": __HTTP_HEADERS__,
                            "body": json.dumps(
                                {'is_done': False}
                            )
                        }

                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(
                        {'is_done': True}
                    )
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no job found with this identifier : {}".format(
                        event['pathParameters']['job'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }
