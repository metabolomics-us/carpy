def history(tableName: str = 'wcmc-data-stasis-ecs-dev'):
    import boto3

    from boto3.dynamodb.types import TypeDeserializer
    from boto3.dynamodb.transform import TransformationInjector

    client = boto3.client('dynamodb')
    paginator = client.get_paginator('scan')
    operation_model = client._service_model.operation_model('Scan')
    trans = TransformationInjector(deserializer=TypeDeserializer())
    operation_parameters = {
        'TableName': tableName
    }
    items = []

    for page in paginator.paginate(**operation_parameters):
        has_last_key = 'LastEvaluatedKey' in page
        if has_last_key:
            last_key = page['LastEvaluatedKey'].copy()
        trans.inject_attribute_value_output(page, operation_model)
        if has_last_key:
            page['LastEvaluatedKey'] = last_key

        for x in page['Items']:
            items.append(x)

    return items
