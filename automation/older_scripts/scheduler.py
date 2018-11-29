#!/usr/bin/env python

import argparse
import requests
import simplejson as json
import time


def create_tasks_stasis(files, args):
    indexed = zip(range(1, len(files) + 1), files)

    tasks = []
    for (idx, file) in indexed:
        if idx < args.start_index:
            continue

        tasks.append({
            'profile': args.platform,
            'env': 'test',
            'sample': file,
            'method': args.method
        })

    return tasks


def create_tasks_carrot(files, args):
    indexed = zip(range(1, len(files) + 1), files)

    tasks = []
    for (idx, file) in indexed:
        if idx < args.start_index:
            continue

        samples = [{'fileName': file,
                    'matrix': {
                        'identifier': None,
                        'species': None,
                        'organ': None,
                        'comment': None,
                        'label': None}
                    }]
        if (args.task.startswith('task')):
            taskName = 'task-' + time.strftime('%Y%m%d') + '-' + str(idx)
        else:
            taskName = args.task + '-' + time.strftime('%Y%m%d') + '-' + str(idx)

        tasks.append({'name': f'{args.submitter}_{taskName}',
                      'email': args.submitter,
                      'acquisitionMethod': {
                          'chromatographicMethod': {
                              'name': args.method,
                              'instrument': None,
                              'column': None,
                              'ionMode': {
                                  'mode': args.ion_mode
                              }
                          },
                          'title': args.method + ' (' + args.ion_mode + ')'
                      },
                      'platform': {'platform': {'name': 'lcms'}},
                      'samples': samples
                      })

    return tasks


def submit(task, api):
    print(f'scheduling task to {api}...')

    if api == 'carrot':
        submission_url = 'http://localhost:18080/rest/schedule'
    else:
        submission_url = 'https://test-api.metabolomics.us/stasis/schedule'

    headers = {'Content-Type': 'application/json'}
    r = requests.post(submission_url, data=json.dumps(task), headers=headers)
    print(r.status_code, r.reason)
    time.sleep(1)  # in seconds, unlike java's millis


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', help='File with a list of samples to schedule', required=True)
    parser.add_argument('-s', '--submitter', help='Submitter\'s email', required=True)
    parser.add_argument('-t', '--task', help='Task name', default='task', type=str)
    parser.add_argument('-p', '--platform', help='Data\'s chromatography type', default='lcms', type=str,
                        choices=['lcms', 'gcms'])
    parser.add_argument('-i', '--ionmode', help='Ion mode of the samples', default='positive',
                        choices=['positive', 'negative'])
    parser.add_argument('-m', '--method', help='Name of the chromatographic method (library)', default='lcms-istds')
    parser.add_argument('-a', '--api', help='Submit the tasks to the selected api: carrot or stasis', default='carrot',
                        choices=['carrot', 'stasis'])
    parser.add_argument('--start_index', help='Starting index (1 to number of files)', default=1, type=int)
    parser.add_argument('--dry_run', help='Do not submit the tasks, just print them', dest='dry', action='store_true')

    args = parser.parse_args()

    data = open(args.files, 'r')
    list = [l for l in (line.strip() for line in data) if l]
    data.close()

    if args.api == 'carrot':
        tasks = create_tasks_carrot(list, args)
    else:
        tasks = create_tasks_stasis(list, args)

    for task in tasks:
        if args.dry:
            print(task)
        else:
            submit(task, args.api)
