import os
import sys
import argparse
import json
from json_parser import json_parse


def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='json_parser_args')
    # set the argument formats
    parser.add_argument(
        '--file', default=os.path.join('.', 'json_files', 'architectures.json'),
        help='json file to be parsed')
    parser.add_argument(
        '--keys', default=['architectureName', 'subContent'],
        help='json file keys to be searched for')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    text = json_parse(args.file, args.keys)
    print('\n'.join(text))