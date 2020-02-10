import os
import sys
import argparse
import json


def json_parse(file):
    out = ''
    json_keys = ['title', 'text']
    with open(file, 'r') as f:
        json_list = json.load(f)
        # For each dictionary in the list...
        for i, d in enumerate(json_list):
            # Get the data dictionary
            data = d.get('data')
            if data is not None:
                for j, val in enumerate(data):
                    if val.get('title') is not None:
                        out += val.get('title') + '\n'
                    if val.get('text') is not None:
                        print(val.get('text'))
                        out += val.get('text') + '\n'

        return out


def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='json_parser_args')
    # set the argument formats
    parser.add_argument(
        '--file', default=os.path.join('.', 'kubernetes.json'),
        help='json file to be parsed')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    text = json_parse(args.file)
    print(text)
