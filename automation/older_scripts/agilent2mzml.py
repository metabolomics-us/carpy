#!/usr/bin/env python

import argparse
import ntpath
import os
import requests
import shutil


def compress(filename, input, output):
    template = f'{os.getcwd()}/{output}/{filename}'
    if (os.path.isfile(f'{template}.zip')):
        zipped = f'{template}.zip'
    else:
        print(f'Compressing {filename}')
        zipped = shutil.make_archive(template, 'zip', input, filename, True)
    return zipped


def convert(zfiles, output):
    baseUrl = "http://phobos.fiehnlab.ucdavis.edu:9090/rest/conversion"

    for zf in zfiles:
        print(f'Converting {zf}...')
        files = {'file': (ntpath.basename(zf), open(zf, 'rb'))}
        res = requests.post(f'{baseUrl}/upload', files=files)
        print(res.status_code)
        print(res.text)
        if (res.status_code == 200):
            mzfile = requests.get(f'{baseUrl}/download/{filename}/mzml')


def process(input, output):
    fnames = os.listdir(input)
    zfiles = []

    for filename in fnames:
        zippedfile = compress(filename, input, output)
        zfiles.append(zippedfile)
    print('...compressed %d files' % len(zfiles))

    convert(zfiles, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input directory')
    parser.add_argument('-o', '--output', default='output', help='Output directory (default: ./output)')
    args = parser.parse_args()

    process(args.input, args.output)
