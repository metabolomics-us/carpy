#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import yaml

from scheduler.scheduler import Scheduler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('file', help='Experiment definition yml or the samples to '
                                     'prepare/schedule', type=str, default='__unknown__')

    parser.add_argument('-t', '--test', help='Test run. Do not submit any data.', action='store_true')

    args = parser.parse_args()
    if args.file == '__unknown__':
        print(parser.print_help())
        SystemExit('Missing experiment folder')
    folder, cfgfile = args.file.rsplit('/', 1)

    print(f'folder: {folder}')
    print(f'file: {args.file}')

    with open(f'{args.file}', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            if args.test:
                config['test'] = True
            else:
                config['test'] = False
        except yaml.YAMLError as exc:
            print(exc)
        except FileNotFoundError as fnf:
            print(f'Can\'t find experiment.yml file\n\tERROR: {fnf}')
            exit(-1)

        if 'env' not in config:
            config['env'] = 'test'
        if 'task_version' not in config:
            config['task_version'] = 164

        sched = Scheduler(config)
        sched.process(folder)
