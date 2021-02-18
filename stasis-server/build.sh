#!/bin/bash

##
# very simple deployment script to upload all our stacks
#
export SLS_DEBUG=*

sls create_domain --config serverless-schedule.yml --stage $1
sls create_domain --config serverless-stasis.yml --stage $1
#
#sls remove --config serverless-schedule.yml --stage $1
#sls remove --config serverless-stasis.yml --stage $1
#sls remove --config serverless-resources.yml --stage $1
#sls remove --config serverless-minix.yml --stage $1

sls deploy --config serverless-resources.yml --stage $1
sls deploy --config serverless-stasis.yml --stage $1
sls deploy --config serverless-schedule.yml --stage $1
sls deploy --config serverless-minix.yml --stage $1




