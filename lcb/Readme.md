# LCB

LCB is the command line driven frontend to interact with the remote lc binbase service. It easily allows you todo the following operations

- schedule a sample for processing
- schedule a job for processing
- query the state of a sample
- query the state of a job
- download a processed datafile
- download a processed result file
- generate compound generation reports


### Requirements

python-3.8

lcb: https://github.com/metabolomics-us/carpy/tree/master/lcb

env variables for applicable 

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

Further operations can be seen by adding '--help' to the lcb command
