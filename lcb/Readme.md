# LCB

LCB is the command line driven frontend to interact with the remote lc binbase service. It easily allows you todo the following operations

- schedule a sample for processing
- schedule a job for processing
- query the state of a sample
- query the state of a job
- download a processed datafile
- download a processed result file
- generate compound generation reports
- run a compute node to process data
- aggregate a specific job
- execute steac calculations

### Requirements

python-3.8

lcb: https://github.com/metabolomics-us/carpy/tree/master/lcb

env variables for application

- STASIS_API_TOKEN 
- STASIS_API_URL


### Local installation

1. create venv

``` 
virtualenv env 
```

2. activate env
```
source env/bin/activate
```
3. install requirements
```
pip install --upgrade -r requirements.txt
```

4. install lcb

```
pip install ./

```

5. set the required variables
```
export STASIS_API_TOKEN=*********<secret>*
export STASIS_API_URL=https://dev-api.metabolomics.us/stasis****
```

These define the evironment you want to be in. Nost of the time this should be either prod-api or dev-api

5. run

```
lcb-client.py <?>
```

### Operations

to import one of the job please execute:
```
lcb job --upload <JOB_FILE> --id <JOB_ID>
```

to start processing execute

```
lcb job --process --id <JOB_ID>
```

to run a local node, to process data locally

```
lcb node --single
```

this will subscribe to the queue and execute received samples in order

Further operations can be seen by adding '--help' to the lcb command


## Deployment on the cluster

If you would like to run LCB on a local docker swarm cluster, we provide you with a complete docker-compose file to ease this process.

#### setup a secret file in the lcb directory of this repo

```json
{
  "STASIS_URL": "****",
  "STASIS_TOKEN": "****",
  "CIS_URL": "****",
  "CIS_TOKEN": "****",
  "AWS_ACCESS_KEY_ID": "****",
  "AWS_SECRET_ACCESS_KEY": "****"
}
```

#### ensure your local docker is in swarm mode

if you have not generated a swarm yet, please initialize it
```
docker swarm init
```

and add your nodes afterrds.

#### deploy the lcb cluster

All these steps need to be executed on the manager node.

```shell script
docker stack deploy -c docker-compose.yml lbc
```

to ensure that all login tokens are correct and that every node ues the latest images, please execute
these two commands.

#### distribute the login token

```shell script
eval $(aws ecr get-login --no-include-email)
docker service update -d -q --with-registry-auth lcb_node
```

#### force update to use the latest image on all nodes
```shell script
docker service update --force lcb_node
```

#### utilize the lcb tool to register a job and schedule it

```shell script
lcb job --upload <JOB_FILE> --id <JOB_ID>
lcb job --process --id <JOB_ID>
```

this will connect to your configured aws service and push the results to the database
in your cluster!