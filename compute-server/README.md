# Readme

This module listens to the general specified queue and computes LC-BinBase results. It is highly scaleable over dozens of nodes
and combines the processing step as well as aggregation steps of LC-BinBase.

It works in direct conjunction with the 'job-server', 'stasis' and 'data-processing' system.

The reasons for breaking this module out, is to allow for the smallest possible requirements for the AWS lambda based
'job-server' module to allow for fast deployment times.

## Requirements

- deployed 'job-server'
- deployed 'stasis-server'