import os
import sys
import argparse
import json


def json_parse(file, key_list):
    with open(file, 'r') as f:
        json_list = json.load(f)
        return recursive_list_unpacker(json_list, key_list)


def recursive_dict_unpacker(json_dict, key_list):
    output = ''
    # Go through the dictionary looking for lists
    for value in json_dict.values():
        if isinstance(value, list):
            # If the value is a list then call the list fn
            output += recursive_list_unpacker(value, key_list)

    # Find matching key pair values
    for i in json_dict:
        if i in key_list:
            output += json_dict.get(i) + '\n'

    return output


def recursive_list_unpacker(json_list, key_list):
    output = ''
    # Go through the list looking for dictionaries
    for i in json_list:
        if isinstance(i, dict):
            # Call recursive dict fn
            output += recursive_dict_unpacker(i, key_list)
    return output


def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='json_parser_args')
    # set the argument formats
    parser.add_argument(
        '--file', default=os.path.join('.', 'json_files', 'kubernetes.json'),
        help='json file to be parsed')
    parser.add_argument(
        '--keys', default=['title', 'text'],
        help='json file keys to be searched for')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    text = json_parse(args.file, args.keys)
    print(text)
