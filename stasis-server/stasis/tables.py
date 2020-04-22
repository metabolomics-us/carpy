import os
import re
import time
from typing import Optional, List

import boto3
import simplejson as json
from boto.dynamodb2.exceptions import ResourceInUseException, ValidationException
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ParamValidationError

from stasis.schedule.backend import Backend, DEFAULT_PROCESSING_BACKEND
from stasis.service.Status import States, FAILED, EXPORTED


class TableManager:

    def __init__(self):
        self.db = boto3.resource('dynamodb', 'us-west-2')

    def get_job_state_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """

        table_name = os.environ['jobStateTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']

        if table_name not in existing_tables:
            try:
                print(self.db.create_table(
                    TableName=os.environ["jobStateTable"],
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'job',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'job',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'state',
                            'AttributeType': 'S'
                        },

                    ],
                    BillingMode='PAY_PER_REQUEST',
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'job-id-state-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'job',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },

                        },

                        {
                            'IndexName': 'state-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'state',
                                    'KeyType': 'HASH'
                                },
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },

                        }
                    ]
                ))
            except ParamValidationError as e:
                raise e

            except ResourceInUseException as e:
                print("table {} exist, ignoring error {}".format(table_name, e))
                pass
            except ValidationException as ex:
                raise ex
            except Exception as ex:
                print("table {} exist, ignoring error {}".format(table_name, ex))
                pass

        return self.db.Table(table_name)

    def get_job_sample_state_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """

        table_name = os.environ['jobTrackingTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']

        if table_name not in existing_tables:
            try:
                print(self.db.create_table(
                    TableName=os.environ["jobTrackingTable"],
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'job',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'job',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'sample',
                            'AttributeType': 'S'
                        },
                    ],
                    BillingMode='PAY_PER_REQUEST',
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'job-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'job',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },

                        },

                        {
                            'IndexName': 'sample-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'sample',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },

                        }
                    ]
                ))
            except ParamValidationError as e:
                raise e
            except ResourceInUseException as e:
                print("table {} exist, ignoring error {}".format(table_name, e))
                pass
            except ValidationException as ex:
                raise ex
            except Exception as ex:
                print("table {} exist, ignoring error {}".format(table_name, ex))
                pass

        return self.db.Table(table_name)

    def generate_job_id(self, job: str, sample: str) -> str:
        """
        generates our job id
        """
        return "{}_{}".format(job, sample)

    def get_tracking_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """

        table_name = os.environ['trackingTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']

        if table_name not in existing_tables:
            try:
                print(self.db.create_table(
                    TableName=os.environ["trackingTable"],
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'experiment',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'experiment',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST',
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'experiment-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'experiment',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },

                        }
                    ]
                ))
            except ParamValidationError as e:
                raise e
            except ResourceInUseException as e:
                print("table {} exist, ignoring error {}".format(table_name, e))
                pass
            except Exception as ex:
                print("table {} exist, ignoring error {}".format(table_name, ex))
                pass

        return self.db.Table(table_name)

    def get_acquisition_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """
        table_name = os.environ['acquisitionTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']
        if table_name not in existing_tables:
            try:
                print(self.db.create_table(
                    TableName=os.environ["acquisitionTable"],
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'experiment',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'experiment',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST',
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'experiment-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'experiment',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },

                        }
                    ])
                )
            except ParamValidationError as e:
                raise e
            except ResourceInUseException as e:
                print("table {} exist, ignoring error {}".format(table_name, e))
                pass
            except Exception as ex:
                print("table already exist, ignoring error {}".format(ex))
                pass

        return self.db.Table(table_name)

    def sanitize_json_for_dynamo(self, result):
        """
        sanitizes a list and makes it dynamo db compatible
        :param result:
        :return:
        """

        from boltons.iterutils import remap

        result = remap(result,
                       visit=lambda path, key, value: True if isinstance(value, (int, float, complex)) else bool(value))
        data_str = json.dumps(result, use_decimal=True)
        new_result = json.loads(data_str, use_decimal=True)

        return new_result


def update_job_state(job: str, state: str, reason: Optional[str] = None):
    """
    updates the state of a job
    """

    tm = TableManager()
    trktable = tm.get_job_state_table()
    states = States()

    result = trktable.query(
        KeyConditionExpression=Key('id').eq(job)
    )

    if "Items" in result and len(result['Items']) > 0:
        item = result['Items'][0]
        old_state = item['state']

        if states.priority(old_state) > states.priority(state):
            print(f"race condition, something already updated this job {job} to newer state!")
            return get_job_state(job)
        if old_state != state:
            item['state'] = str(state)
            ts = _compute_state_change(item, old_state, state)

            item['timestamp'] = ts
            item["reason"] = reason

            body = tm.sanitize_json_for_dynamo(item)
            saved = trktable.put_item(Item=body)  # save or update our item

            saved = saved['ResponseMetadata']

            saved['statusCode'] = saved['HTTPStatusCode']

        return get_job_state(job)
    else:
        print("no job update was required for {}".format(job))
        return None


def _compute_state_change(item, old_state, state):
    ts = time.time() * 1000
    if 'durations' not in item:
        item['durations'] = {}
    if 'past_states' not in item:
        item['past_states'] = []

    if old_state in item['past_states']:
        # already got this state no need to refresh it
        # todo correct would be to replace it and update
        # the timestamp accordingly
        return ts
    item['past_states'].append(old_state)
    item['durations']["{}->{}".format(old_state, item['state'])] = {
        "seconds": (float(ts) - float(item['timestamp'])) / 1000,
        "state_previous": old_state,
        "state_current": str(state)
    }
    return ts


def set_job_state(job: str, env: str, method: str, profile: str, state: str,
                  reason: Optional[str] = None, resource: Optional[Backend] = None):
    """
    sets the state in the job table for the given sample and job
    """
    if reason is None:
        return _set_job_state(
            body={"job": job, "id": job, "state": str(state), "method": method,
                  "profile": profile, "env": env, "resource": resource})
    else:
        return _set_job_state(
            body={"job": job, "id": job, "state": str(state), "method": method,
                  "profile": profile, "reason": str(reason), "env": env, "resource": resource})


def get_job_config(job: str) -> Optional[dict]:
    """
    returns the basic config of a job
    """
    try:
        tm = TableManager()
        trktable = tm.get_job_state_table()

        query_params = {
            'IndexName': 'job-id-state-index',
            'Select': 'ALL_ATTRIBUTES',
            'KeyConditionExpression': Key('job').eq(job)
        }
        result = trktable.query(
            **query_params
        )

        if "Items" in result and len(result['Items']) > 0:
            item = result['Items'][0]

            if 'resource' in item:
                item['resource'] = Backend(item['resource'])
            else:
                item['resource'] = DEFAULT_PROCESSING_BACKEND
            return item
        else:
            return None
    except Exception as e:
        raise e


def get_job_state(job: str) -> Optional[str]:
    """
    returns the state of the job
    """
    try:
        tm = TableManager()
        trktable = tm.get_job_state_table()

        query_params = {
            'IndexName': 'job-id-state-index',
            'Select': 'ALL_ATTRIBUTES',
            'KeyConditionExpression': Key('job').eq(job)
        }
        result = trktable.query(
            **query_params
        )

        if "Items" in result and len(result['Items']) > 0:
            item = result['Items'][0]
            return item['state']
        else:
            return None
    except Exception as e:
        raise e


def _set_job_state(body: dict):
    timestamp = int(time.time() * 1000)

    body['timestamp'] = timestamp

    if 'resource' in body and body['resource'] is not None:
        body['resource'] = body['resource'].value
    else:
        body['resource'] = DEFAULT_PROCESSING_BACKEND.value

    tm = TableManager()
    t = tm.get_job_state_table()

    body = tm.sanitize_json_for_dynamo(body)
    saved = t.put_item(Item=body)  # save or update our item

    saved = saved['ResponseMetadata']

    saved['statusCode'] = saved['HTTPStatusCode']

    return saved


def set_sample_job_state(sample: str, job: str, state: str, reason: Optional[str] = None):
    """
    sets the state in the job table for the given sample and job
    """
    if reason is None:
        return _set_sample_job_state(body={"job": job, "sample": sample, "state": str(state)})
    else:
        return _set_sample_job_state(body={"job": job, "sample": sample, "state": str(state), "reason": str(reason)})


def _set_sample_job_state(body: dict):
    ts = None
    tm = TableManager()
    body['id'] = tm.generate_job_id(body['job'], body['sample'])
    trktable = tm.get_job_sample_state_table()

    #   result = trktable.query(
    #       KeyConditionExpression=Key('id').eq(body['id'])
    #   )

    #   if body['state'] != SCHEDULED:
    #       if "Items" in result and len(result['Items']) > 0:
    #           item = result['Items'][0]
    #           body['timestamp'] = item['timestamp']
    #           ts = _compute_state_change(body, item['state'], body['state'])

    if ts is None:
        ts = int(time.time() * 1000)
    body['timestamp'] = ts
    body = tm.sanitize_json_for_dynamo(body)
    saved = trktable.put_item(Item=body)  # save or update our item

    save_sample_state(sample=body['sample'], state=body['state'], reason=body.get('reason'),
                      fileHandle=body.get('fileHandle'))
    saved = saved['ResponseMetadata']

    saved['statusCode'] = saved['HTTPStatusCode']

    return saved


def load_jobs_for_sample(sample: str) -> Optional[List[dict]]:
    """
    loads all jobs for the specified sample
    :param sample:
    :return:
    """

    tm = TableManager()
    table = tm.get_job_sample_state_table()

    query_params = {
        'IndexName': 'sample-id-index',
        'Select': 'ALL_ATTRIBUTES',
        'KeyConditionExpression': Key('sample').eq(sample)
    }
    result = table.query(**query_params
                         )

    if "Items" in result and len(result['Items']) > 0:
        data = []
        for x in result['Items']:
            try:
                job_id = x['job']
                data.append(get_job_config(job=job_id))
            except Exception as e:
                print("might be related to a job [{}] not found {}".format(x, str(e)))
                pass

        return data
    else:
        return None


def load_job_samples(job: str) -> Optional[dict]:
    """
    loads the job from the job table for the given name
    """

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
        results = {}
        for x in result['Items']:
            # get stasis state here
            results[x['sample']] = get_tracked_state(x['sample'])
        return results

    else:
        return None


def get_tracked_sample(sample: str) -> Optional[dict]:
    """
    this returns the complete sample definition for the given sample or none from the stasis tracking table
    this is the heart of the synchronization system
    """

    tm = TableManager()
    table = tm.get_tracking_table()
    key = sample.split(".")[0]

    result = table.query(
        KeyConditionExpression=Key('id').eq(key)
    )

    if 'Items' in result and len(result['Items']) > 0:
        return result['Items'][0]
    else:
        return None


def get_tracked_state(sample: str) -> Optional[str]:
    """
    returns the state of a sample in stasis
    """

    data = get_tracked_sample(sample)

    if data is None:
        return None
    else:
        states = data['status']
        state = states[-1]
        return state['value']


def get_file_handle(sample: str, state: str = "exported") -> Optional[str]:
    """
    returns the file handle for the given sample and state
    """

    # TODO needs a real implemenations by looking it up from stasis tracking data. Just a dummy solution for now
    if state == 'converted':
        return "{}.mzml".format(sample)
    elif state == 'exported':
        return "{}.mzml.json".format(sample)

    raise Exception("not supported file handle!")


def get_file_by_handle(fileHandle: str) -> Optional[str]:
    """
    returns the file name as specified by this handle
    :param fileHandle:
    :return:
    """
    if fileHandle.endswith(".mzml.json"):
        return fileHandle.replace(".mzml.json", "")

    raise Exception("not supported file handle!")


def save_sample_state(sample: str, state: str, fileHandle: Optional[str] = None, reason: Optional[str] = None):
    status_service = States()
    if not status_service.valid(state):
        raise Exception("please provide the a valid 'state', you provided {}".format(state))
    # if validation passes, persist the object in the dynamo db
    tm = TableManager()
    table = tm.get_tracking_table()
    resp = table.query(
        KeyConditionExpression=Key('id').eq(sample)
    )
    timestamp = int(time.time() * 1000)
    experiment = _fetch_experiment(sample)
    new_status = {
        'time': timestamp,
        'value': state.lower(),
        'priority': status_service.priority(state),
    }

    if fileHandle is not None:
        new_status['fileHandle'] = fileHandle
    if reason is not None:
        new_status['reason'] = reason

    if resp['Items']:
        # only keep elements with a lower priority
        item = resp['Items'][0]
        item['status'] = [x for x in item['status'] if int(x['priority']) < int(new_status['priority'])]
    else:
        item = {
            'id': sample,
            'sample': sample,
            'experiment': experiment,
            'status': []
        }

    if len(item['status']) > 0:
        previous = item['status'][-1]
        # update if no previous file handle is set
        if fileHandle is not None:
            if 'fileHandle' not in previous:
                if previous['value'] != 'entered':
                    previous['fileHandle'] = fileHandle

        # update if previous file handle is set, but no new one was added
        else:
            if 'fileHandle' in previous:
                new_status['fileHandle'] = previous['fileHandle']

    # register the new state
    item['status'].append(new_status)

    item = tm.sanitize_json_for_dynamo(item)
    # put item in table instead of queueing
    saved = {}
    try:
        saved = table.put_item(Item=item)

        # FAILED => sync
        # SCHEDULED => sync
        # EXPORTED => sync
        # this should avoid potential dead lock issue
        if state in [FAILED, EXPORTED]:
            from stasis.jobs.sync import sync_sample
            ##
            # TODO push this to a queue to increase responsivness
            sync_sample(sample)
        else:
            print("triggered state {} did not require job synchronization for sample {}".format(state, sample))
    except Exception as e:
        print("ERROR: %s" % e)
        item = {}
        saved['ResponseMetadata']['HTTPStatusCode'] = 500
    return item, saved


def _fetch_experiment(sample: str) -> str:
    """
        loads the internal experiment id for the given sample
    :param sample:
    :return:
    """
    print("\tfetching experiment id for sample %s" % sample)
    tm = TableManager()
    acq_table = tm.get_acquisition_table()

    result = acq_table.query(
        KeyConditionExpression=Key('id').eq(_remove_reinjection(sample))
    )

    if result['Items']:
        item = result['Items'][0]
        if 'experiment' in item:
            return item['experiment']
        else:
            print('no experiment in item -> unknown')
    else:
        #        print('no items -> unknown')
        pass

    return 'unknown'


def _remove_reinjection(sample: str) -> str:
    # cleaned = re.split('[A-Za-z]+(\d{3,4}|_MSMS)_MX\d+_[A-Za-z]+_[A-Za-z0-9-]+(_\d+_\d+)?', sample, 1)
    cleaned = re.split(r'_\d|_BU', sample)[0]

    return cleaned
