# Stasis Server


## Plugins

first you need to install all required serverless plugins

```
sls plugin install -n serverless-domain-manager
sls plugin install -n serverless-python-requirements
sls plugin install -n serverless-aws-documentation
sls plugin install -n serverless-plugin-split-stacks
```

## Delete Log groups

```
export AWS_DEFAULT_REGION=us-west-2
aws logs describe-log-groups --query 'logGroups[*].logGroupName' --output table | \
awk '{print $2}' | grep ^/aws/lambda | while read x; do  echo "deleting $x" ; aws logs delete-log-group --log-group-name $x; done
```

shamelessly liberated from the internet

## Running integration tests

These tests require the `STASIS_API_TOKEN` environmental variable to be set or, alternatively, to be defined in a `test.env` file in the project root.


## Create Resources, if required

if you have not yet created any resources for the given stage, please do the following

cd resources

`sls deploy --stage <NAME>`

which will setup required queues and so for you. Please be aware, if any of the resources already exist, this will fail
with useless error messages instead of ignoring existing resources.

Thank you serverless!

https://github.com/serverless/serverless/issues/3183

## Deploy Stasis

### Option 1

run `build.sh <STAGE>`

Where <STAGE> is one of test, dev or prod

### Option 2

if no domain is setup:

```
serverless create_domain --stage <STAGE> -c serverless-schedule.yml
serverless create_domain --stage <STAGE> -c serverless-stasis.yml
```

this only needs to be done once and might take 45m until the service is registered. Also ensure that your certificate is
setup for this domain!

The following needs to be run in the specified order:

```
sls deploy --stage <STAGE> -c serverless-resources.yml
sls deploy --stage <STAGE> -c serverless-stasis.yml
sls deploy --stage <STAGE> -c serverless-schedule.yml
sls deploy --stage <STAGE> -c serverless-minix.yml
```

deploys the stage, assuming you setup the domain

## Build documentation

Run one of the following commands to create an openapi file in the preferred format:

### Yaml

`aws apigateway get-export --rest-api-id <api-id> --stage-name <stage> --export-type oas30 --accepts 'application/yaml' openapi.yml`

### JSON

`aws apigateway get-export --rest-api-id <api-id> --stage-name <stage> --export-type oas30 openapi.json`

To view the documentation copy the contents of the file and paste on the left panel at: https://editor.swagger.io/
