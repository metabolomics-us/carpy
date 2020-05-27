from stasis.schedule.tracking import ecs


def test_ecs_correct_event(requireMocking):
    event = {'version': '0', 'id': 'a136dee7-d767-03b8-ec66-ad92a0cffa64', 'detail-type': 'ECS Task State Change',
             'source': 'aws.ecs', 'account': '702514165722', 'time': '2020-05-26T20:23:52Z', 'region': 'us-west-2',
             'resources': ['arn:aws:ecs:us-west-2:702514165722:task/1e49b6c0-398b-4ce4-af40-5bf864225b86'], 'detail': {
            'attachments': [{'id': '3791b31f-2e51-463f-9145-5c80efaeee1d', 'type': 'eni', 'status': 'DELETED',
                             'details': [{'name': 'subnetId', 'value': 'subnet-04c0515e'},
                                         {'name': 'networkInterfaceId', 'value': 'eni-0f3311da2ff0907e9'},
                                         {'name': 'macAddress', 'value': '0a:93:3d:67:e8:5c'},
                                         {'name': 'privateIPv4Address', 'value': '172.31.2.224'}]}],
            'availabilityZone': 'us-west-2c', 'clusterArn': 'arn:aws:ecs:us-west-2:702514165722:cluster/carrot',
            'containers': [
                {'containerArn': 'arn:aws:ecs:us-west-2:702514165722:container/1f5c6d19-fb36-4416-9bf7-7cb93cba51e1',
                 'exitCode': 1, 'lastStatus': 'STOPPED', 'name': 'carrot-runner',
                 'image': '702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:latest',
                 'imageDigest': 'sha256:b164e960c20f1bb52ad48646249c5133f8192b0ec5bf88204cb301401ba95325',
                 'runtimeId': 'a712701f23baa1c6d605487bac0ba27325617193d219b4e8aa210a334229ceb2',
                 'taskArn': 'arn:aws:ecs:us-west-2:702514165722:task/1e49b6c0-398b-4ce4-af40-5bf864225b86',
                 'networkInterfaces': [
                     {'attachmentId': '3791b31f-2e51-463f-9145-5c80efaeee1d', 'privateIpv4Address': '172.31.2.224'}],
                 'cpu': '0'}], 'createdAt': '2020-05-26T20:21:55.847Z', 'launchType': 'FARGATE', 'cpu': '1024',
            'memory': '8192', 'desiredStatus': 'STOPPED', 'group': 'family:test-secure-carrot-runner',
            'lastStatus': 'STOPPED', 'overrides': {'containerOverrides': [{'environment': [
                {'name': 'SPRING_PROFILES_ACTIVE', 'value': 'awstest,carrot.lcms'},
                {'name': 'CARROT_SAMPLE', 'value': 'B10A_SA8922_TeddyLipids_Pos_122WP.mzml'},
                {'name': 'CARROT_METHOD', 'value': 'teddy | 6530 | test | positive'},
                {'name': 'CARROT_MODE', 'value': 'carrot.lcms'},
                {'name': 'STASIS_KEY', 'value': '9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi'}],
                                                                           'name': 'carrot-runner'}]},
            'connectivity': 'CONNECTED', 'connectivityAt': '2020-05-26T20:22:02.243Z',
            'pullStartedAt': '2020-05-26T20:22:13.623Z', 'startedAt': '2020-05-26T20:22:48.623Z',
            'stoppingAt': '2020-05-26T20:23:37.451Z', 'stoppedAt': '2020-05-26T20:23:52.228Z',
            'pullStoppedAt': '2020-05-26T20:22:48.623Z', 'executionStoppedAt': '2020-05-26T20:23:27Z',
            'stoppedReason': 'Essential container in task exited', 'stopCode': 'EssentialContainerExited',
            'updatedAt': '2020-05-26T20:23:52.228Z',
            'taskArn': 'arn:aws:ecs:us-west-2:702514165722:task/1e49b6c0-398b-4ce4-af40-5bf864225b86',
            'taskDefinitionArn': 'arn:aws:ecs:us-west-2:702514165722:task-definition/test-secure-carrot-runner:8',
            'version': 6, 'platformVersion': '1.3.0'}}

    ecs(event, {})
