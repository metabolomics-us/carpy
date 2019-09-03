#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import yaml

from scheduler.scheduler import Scheduler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('file', help='Folder containing the experiment definition yaml or the samples to '
                                     'prepare/schedule', type=str, default='__unknown__')
    # parser.add_argument('-e', '--experiment', help='Name of the experiment.', required=True)
    # parser.add_argument('-i', '--instrument', help='Name of the instrument used.', required=True)
    # parser.add_argument('-c', '--column', help='Name of the column used.', default='test')
    # parser.add_argument('-m', '--method', help='Annotation library name.', required=True)
    # parser.add_argument('-n', '--ion_mode', help='Ionization mode.', choices=['positive', 'negative'],
    #                     default='positive')
    # parser.add_argument('-s', '--species', help='Species the sample comes from.', default='human')
    # parser.add_argument('-o', '--organ', help='Organ from which the sample was extracted.', default='plasma')
    # parser.add_argument('-a', '--acquisition', help='Creates acquisition metadata for each file.', action='store_true')
    # parser.add_argument('-v', '--task_version', help='Submits the sample to a specific task revision.', default='163')
    # parser.add_argument('-x', '--extra_profiles', help='Comma separated list of extra profiles to pass to springboot.')
    # parser.add_argument('-p', '--prepare', help='Pre-loads the acquisition data of samples.', action='store_true')
    # parser.add_argument('-r', '--schedule', help='Schedules the processing of samples.', action='store_true')
    parser.add_argument('-t', '--test', help='Test run. Do not submit any data.', action='store_true')
    # parser.add_argument('--msms', help='Flags the runner in the cloud to process MSMS spectra.', action='store_true')

    args = parser.parse_args()
    if args.file == '__unknown__':
        print(parser.print_help())
        SystemExit('Missing experiment folder')
    folder = args.file.rstrip('/')

    with open(f'{folder}/experiment.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            if args.test:
                config['test'] = True
            else:
                config['test'] = False

        except yaml.YAMLError as exc:
            print(exc)
        except FileNotFoundError as fnf:
            print(f'Can\'t find experiment.yaml file\n\tERROR: {fnf}')
            exit(-1)

        sched = Scheduler(config)
        sched.process(folder)
