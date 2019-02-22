import argparse

from crag import aggregator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('infiles', nargs='+', metavar='FILE', type=str,
                        help='full filename of the text files containing the list of samples (one per line) to '
                             'aggregate.')
    parser.add_argument('-e', '--experiment', help='name of the experiment to aggregate results', required=False)
    parser.add_argument('-t', '--test', help='Test mode. Run with only a few samples', action='store_true')
    parser.add_argument('-l', '--log', help='Log stasis responses', action='store_true')

    try:
        args = parser.parse_args()
        aggregator.aggregate(args)

    except Exception as ex:
        print(str(ex.args))
        parser.print_help()
        exit(-1)
