# Set AWS environment variables if they don't exist before importing moto/boto3
import os

if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

if 'PROD_STASIS_API_TOKEN' not in os.environ:
    os.environ['PROD_STASIS_API_TOKEN'] = 'GUec9mh1jc6VFbudSzxfz8aIqdRiadqw6wWBzRCB'
