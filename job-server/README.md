# Readme

This tool provides an AWS lambda based API to schedule samples with LC-BinBase for data processing. Internally it delegates parts of this
to the following the 'compute-server' module in the same git repository.

This external module will do the actual computation and scaling, to allow the concurrent processing of 1000s of samples at a time and their aggregation.

## Requirements

1. npm install serverless-domain-manager --save-dev
2. npm install serverless-python-requirements --save-dev
3. npm install serverless-aws-documentation --save-dev
4. create the required bucket, as configured in the serverless yaml file


## Deployment

sls deploy --stage prod | dev | test

## Generating Documentation

serverless downloadDocumentation --outputFileName=filename.yml