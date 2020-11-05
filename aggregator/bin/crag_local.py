#!/usr/bin/env python
import argparse

from crag.aggregator import Aggregator


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--files', nargs='*', type=str, required=False, dest='infiles',
                        help='full filename of the text files containing the list of samples (one per line) to '
                             'aggregate.')
    parser.add_argument('-e', '--experiment', help='name of the experiment to aggregate results', required=False)
    parser.add_argument('-t', '--test', help='Test mode. Run with only a few samples', action='store_true')
    parser.add_argument('-zr', '--zero-replacement', help='Include replaced intensity values', action='store_true')
    parser.add_argument('-l', '--log', help='Log stasis responses', action='store_true')
    parser.add_argument('-u', '--unknowns', help='save unconfirmed targets', action='store_true', default='false')

    parser.add_argument('-d', '--dir', help='local directory with results files')
    parser.add_argument('-s', '--save', help='save results files to local directory (requires --dir)',
                        action='store_true')
    parser.add_argument('--keep-msms', help='reports msms spectra for all samples containing msms data.',
                        action='store_true')

    parser.add_argument('--mz-tolerance', help='m/z alignment tolerance', type=float, default=0.01)
    parser.add_argument('--rt-tolerance', help='retention time alignment tolerance', type=float, default=0.1)
    return parser


if __name__ == '__main__':
    parser = create_parser()

    args = parser.parse_args()

    # Validate arguments
    if args.save and not args.dir:
        parser.error('--save argument requires a local directory to be provided with --dir')

    # try:
    Aggregator(vars(args)).aggregate()
    # except Exception as ex:
    #     print(str(ex.args))
    #     parser.print_help()
    #     exit(-1)
