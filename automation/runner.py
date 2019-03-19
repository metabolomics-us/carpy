#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from scheduler import scheduler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('file', help='Filename with list of samples to prepare/schedule', type=str, default='__unknown__')
    parser.add_argument('-e', '--experiment', help='Name of the experiment.', required=True)
    parser.add_argument('-i', '--instrument', help='Name of the instrument used.', required=True)
    parser.add_argument('-c', '--column', help='Name of the column used.', default='test')
    parser.add_argument('-m', '--method', help='Annotation library name.', required=True)
    parser.add_argument('-n', '--ion_mode', help='Ionization mode.', choices=['positive','negative'], default='positive')
    parser.add_argument('-s', '--species', help='Species the sample comes from.', default='human')
    parser.add_argument('-o', '--organ', help='Organ from which the sample was extracted.', default='plasma')
    parser.add_argument('-a', '--acquisition', help='Creates acquisition metadata for each file', action='store_true')
    parser.add_argument('-v', '--task_version', help='Submits the sample to a specific task revision', default='160')
    parser.add_argument('-x', '--extra_profiles', help='Comma separated list of extra profiles to pass to springboot')
    parser.add_argument('-p', '--prepare', help='Preloads the acquisition data of samples', action='store_true')
    parser.add_argument('-r', '--schedule', help='Schedules the processing of samples', action='store_true')
    parser.add_argument('-t', '--test', help='Test run. Do not submit any data.', action='store_true')

    args = parser.parse_args()
    if args.file == '__unknown__':
        print(parser.print_help())
        SystemExit('Missing file to process')

    scheduler.process(args)
