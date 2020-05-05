# Stasis Server


## Plugins

first you need to install all required serverless plugins

```
sls plugin install -n serverless-domain-manager
sls plugin install -n serverless-python-requirements
sls plugin install -n serverless-aws-documentation
sls plugin install -n serverless-plugin-split-stacks

```

## Running integration tests

These tests require the `STASIS_API_TOKEN` environmental variable to be set or, alternatively, to be defined in a `test.env` file in the project root.


## Create Resources, if required

if you have not yet created any resources for the given stage, please do the following

cd rsources

sls deploy --stage <NAME>

which will setup required queues and so for you. Please be aware, if any of the resources already exist, this will fail with useless error messages
instead of ignoring existing resources.

Thank you serverless!

https://github.com/serverless/serverless/issues/3183

## Deploy Stasis


if no domain is setup:

serverless create_domain --stage <NAME>

this only needs to be done once and might take 45m until the service is registered. Also ensure that your certificate is setup for this domain!

sls deploy --stage <NAME>

deploys the stage, assuming you setup the domain
