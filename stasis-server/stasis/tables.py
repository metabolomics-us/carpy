import os
import time
from typing import Optional, List

import boto3
import simplejson as json
from boto.dynamodb2.exceptions import ResourceInUseException, ValidationException
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ParamValidationError

from stasis.jobs.states import States


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


def update_job_state(job: str, state: States, reason: Optional[str] = None):
    """
    updates the state of a job
    """

    tm = TableManager()
    trktable = tm.get_job_state_table()

    result = trktable.query(
        KeyConditionExpression=Key('id').eq(job)
    )

    if "Items" in result and len(result['Items']) > 0:
        item = result['Items'][0]
        old_state = item['state']

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
        return None


def _compute_state_change(item, old_state, state):
    ts = time.time() * 1000
    if 'durations' not in item:
        item['durations'] = {}
    if 'past_states' not in item:
        item['past_states'] = []
    item['past_states'].append(old_state)
    item['durations']["{}->{}".format(old_state, item['state'])] = {
        "seconds": (float(ts) - float(item['timestamp'])) / 1000,
        "state_previous": old_state,
        "state_current": str(state)
    }
    return ts


def set_job_state(job: str, env: str, method: str, profile: str, state: States,
                  reason: Optional[str] = None, resource: Optional[str] = None):
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
            return item
        else:
            return None
    except Exception as e:
        raise e


def get_job_state(job: str) -> Optional[States]:
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
            return States[item['state'].upper()]
        else:
            return None
    except Exception as e:
        raise e


def _set_job_state(body: dict):
    timestamp = int(time.time() * 1000)

    body['timestamp'] = timestamp
    tm = TableManager()
    t = tm.get_job_state_table()

    body = tm.sanitize_json_for_dynamo(body)
    saved = t.put_item(Item=body)  # save or update our item

    saved = saved['ResponseMetadata']

    saved['statusCode'] = saved['HTTPStatusCode']

    return saved


def set_sample_job_state(sample: str, job: str, state: States, reason: Optional[str] = None):
    """
    sets the state in the job table for the given sample and job
    """
    if reason is None:
        return _set_sample_job_state(body={"job": job, "sample": sample, "state": str(state)})
    else:
        return _set_sample_job_state(body={"job": job, "sample": sample, "state": str(state), "reason": str(reason)})


def update_sample_state(sample: str, state: States, reason: Optional[str] = None) -> List[str]:
    """
    updates the state for this sample in the job tracking table to ensure it's up to date. Since it's called without a job id, it will updates all related jobs. So it's expensive and can take
    quite a while
    :param sample:
    :param state:
    :param reason:
    :return: list of job id's affected by this change
    """

    # 1. query sample tracking table to get all job ids

    # 2. updated the state accordingly

    # 3. return affect sample id's

    # 4. technically we should modify stasis states, but I don't think we want todo this....


def _set_sample_job_state(body: dict):
    ts = None
    tm = TableManager()
    body['id'] = tm.generate_job_id(body['job'], body['sample'])
    trktable = tm.get_job_sample_state_table()

    result = trktable.query(
        KeyConditionExpression=Key('id').eq(body['id'])
    )

    if body['state'] != States.SCHEDULED.value:
        if "Items" in result and len(result['Items']) > 0:
            item = result['Items'][0]
            body['timestamp'] = item['timestamp']
            ts = _compute_state_change(body, item['state'], body['state'])

    if ts is None:
        ts = int(time.time() * 1000)
    body['timestamp'] = ts
    body = tm.sanitize_json_for_dynamo(body)
    saved = trktable.put_item(Item=body)  # save or update our item

    saved = saved['ResponseMetadata']

    saved['statusCode'] = saved['HTTPStatusCode']

    return saved


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
            results[x['sample']] = x['state']
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
