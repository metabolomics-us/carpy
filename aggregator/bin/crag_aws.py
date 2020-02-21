import argparse
import os

from crag.aws import JobAggregator


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--job', type=str, help='This is the job you would like to process', required=True)
    parser.add_argument('-zr', '--zero-replacement', help='Include replaced intensity values', action='store_true',
                        default=True)
    parser.add_argument('-u', '--upload', help='uploads results to S3',
                        action='store_true', default=True)

    parser.add_argument('--mz-tolerance', help='m/z alignment tolerance', type=float, default=0.01)
    parser.add_argument('--rt-tolerance', help='retention time alignment tolerance', type=float, default=0.1)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    JobAggregator(vars(args)).aggregate_job(job=args.job, upload=args.upload)
