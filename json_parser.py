import os
import sys
import argparse
import json

def json_parse(file):



def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='json_parser_args')
    # set the argument formats
    parser.add_argument(
        '--filepath', '--file', default= os.path.join('.', 'kubernetes.json'),
        help='json file to be parsed')


    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    text = json_parse(args.file)