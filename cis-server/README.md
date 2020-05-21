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

serverless create_domain --stage <NAME>

this only needs to be done once and might take 45m until the service is registered. Also ensure that your certificate is setup for this domain!

sls deploy --stage <NAME>

deploys the stage, assuming you setup the domain
