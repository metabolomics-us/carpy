def schedule_event_to_queue(event, context):
    pass


def schedule_queue_event_to_fargate(event, context):
    """
    triggers a new calculation task on the fargate server
    :param event:
    :param context:
    :return:
    """
    """
        submits a new task to the cluster - a fargate task will run it

    :param configuration:
    :param user:
    :return:
    """
    import boto3
    overrides = {"containerOverrides": [{
        "name": "carrot-runner",
        "environment": [
            {
                "name": "ACTIVE_PROFILE",
                "value": "{}".format("test_profile")
            },
            {
                "name": "CARROT_SAMPLE",
                "value": "{}".format("test_sample")
            },
            {
                "name": "CARROT_METHOD",
                "value": "{}".format("test_method")
            }
        ]
    }]}

    # fire AWS fargate instance now
    client = boto3.client('ecs')
    response = client.run_task(
        cluster='carrot',  # name of the cluster
        launchType='FARGATE',
        taskDefinition='carrot-process:1',
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    # we need at least 2, to insure network stability
                    os.environ.get('FREQ_SUBNET_1', 'subnet-c35bdcab'),
                    os.environ.get('FREQ_SUBNET_2', 'subnet-be46b9c4'),
                    os.environ.get('FREQ_SUBNET_3', 'subnet-234ab559'),
                    os.environ.get('FREQ_SUBNET_4', 'subnet-234ab559')],
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides=overrides,
    )
    return response
