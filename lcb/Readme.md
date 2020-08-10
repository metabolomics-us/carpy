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