# CIS - Server, Compound identification system

This server will provide an easy to use REST api, to interface with the internal postgres
database system to list and modify targets.


## Plugins

first you need to install all required serverless plugins

```
sls plugin install -n serverless-domain-manager
sls plugin install -n serverless-python-requirements
sls plugin install -n serverless-aws-documentation
```


## Running integration tests

runs all relevant integration tests


## Deploy CIS:

if no domain is setup:

`sls create_domain --stage <NAME>`

this only needs to be done once and might take 45m until the service is registered. Also ensure that your certificate is
setup for this domain!

`sls deploy --stage <NAME>`

deploys the stage, assuming you setup the domain

## Build documentation

Run one of the following commands to create an openapi file in the preferred format:

### Yaml

`aws apigateway get-export --rest-api-id <api-id> --stage-name <stage> --export-type oas30 --accepts 'application/yaml' openapi.yml`

### JSON

`aws apigateway get-export --rest-api-id <api-id> --stage-name <stage> --export-type oas30 openapi.json`

To view the documentation copy the contents of the file and paste on the left panel at: https://editor.swagger.io/
