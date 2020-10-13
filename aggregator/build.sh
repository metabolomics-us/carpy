`aws ecr get-login --no-include-email --region us-west-2`
docker build --no-cache -t 702514165722.dkr.ecr.us-west-2.amazonaws.com/agg:latest -f DockerfileAWS .
docker push 702514165722.dkr.ecr.us-west-2.amazonaws.com/agg:latest
