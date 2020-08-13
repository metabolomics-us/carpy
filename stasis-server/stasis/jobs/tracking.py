import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager, _set_sample_job_state, get_tracked_sample, update_job_state


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

            print(event)
            if 'body' in event and event.get("httpMethod","") != 'GET':
                content = json.loads(event['body'])

                result = update_job_state(job, content['job_state'], content.get("reason", ""))
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({
                        "job_state": result,
                        "job_info": result
                    }
                    )
                }
            else:
                job_state = table_overall_state.query(
                    **{
                        'IndexName': 'job-id-state-index',
                        'Select': 'ALL_ATTRIBUTES',
                        'KeyConditionExpression': Key('job').eq(job)
                    }
                )

                # this queries the state of all the samples
                if "Items" in job_state and len(job_state['Items']) > 0:
                    job_state = job_state["Items"]

                    if len(job_state) > 0:
                        job_state = job_state[0]
                        return {
                            "statusCode": 200,
                            "headers": __HTTP_HEADERS__,
                            "body": json.dumps({
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

            if 'psize' in event['pathParameters']:
                page_size = int(event['pathParameters']['psize'])
            else:
                page_size = 10

            query_params = {
                'IndexName': 'job-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('job').eq(job),
                'Limit': page_size
            }

            if 'last_key' in event['pathParameters']:
                print("pagination mode...")

                query_params['ExclusiveStartKey'] = {
                    "job": job,
                    "id": event['pathParameters']['last_key']
                }

            result = table.query(**query_params
                                 )

            if "Items" in result and len(result['Items']) > 0:

                # here we now need to reference the actual stasis tracking table
                result = result['Items']

                # kinda expensive and should be avoided
                for x in result:
                    x['history'] = get_tracked_sample(x['sample'])['status']
                    x['state'] = max(x['history'], key=lambda y: y['priority'])['value']

                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(
                        result
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
