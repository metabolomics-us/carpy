#!/bin/bash
`aws ecr get-login --no-include-email --region us-west-2`
docker build . -t 702514165722.dkr.ecr.us-west-2.amazonaws.com/lcb:latest
docker push 702514165722.dkr.ecr.us-west-2.amazonaws.com/lcb:latest
