# Stasis Server


## Plugins

first you need to install all required serverless plugins

## Running integration tests

These tests require the `STASIS_API_TOKEN` environmental variable to be set or, alternatively, to be defined in a `test.env` file in the project root.

## Deploy Stasis


if no domain is setup:

serverless create_domain --stage <NAME>

this only needs to be done once and might take 45m until the service is registered. Also ensure that your certificate is setup for this domain!

sls deploy --stage <NAME>

deploys the stage, assuming you setup the domain