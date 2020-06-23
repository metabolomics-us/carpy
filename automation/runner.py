#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

import yaml
from stasis_client.client import StasisClient

from scheduler.scheduler import Scheduler


def create_stasis_instance(config):
    if 'env' in config and config['env'] == 'prod':
        url = 'https://api.metabolomics.us/stasis'
    else:
        url = f'https://{config["env"].lower()}-api.metabolomics.us/stasis'
    key_name = f'{config["env"].upper()}_STASIS_API_TOKEN'
    key = os.environ[key_name].strip()

    print(f'Stasis api address: {url}')
    print(f'Stasis api key from: {key_name} = {key}')

    return StasisClient(url, key)


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

        sched = Scheduler(config, create_stasis_instance(config))
        sched.process(folder)
