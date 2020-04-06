# *C*arrot *R*esult *Ag*gregator (crag)
Fetches aggregates the results from AWS's S3 bucket wcmc-data-stasis-result

## Files
- Launcher: cragLauncher.py
- Main module: crag/ folder

## Usage

This system allows you to assemble a zipped result file from several samples. Which are stored on AWS. Once the process is finished
it will automatically upload it to AWS in the result bucket. As specified by stasis.

## AWS deployment

1, build and tag the docker image

```
docker build --no-cache -t 702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:agg-latest -f DockerfileAWS .
```

2. push it to AWS

This might require you to login into ECR first

```.env
docker push 702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:agg-latest
```