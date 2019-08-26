import argparse
import os

from merger.Merger import Merger


def process(filename):
    merger = Merger()
    final = merger.merge_file(filename)

    Merger.save_report(final, os.path.abspath(filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='full path of the file to merge')

    args = parser.parse_args()

    process(args.filename)
