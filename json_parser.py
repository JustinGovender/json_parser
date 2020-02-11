import os
import sys
import argparse
import json
import pandas as pd
from google_api import google_translate
import re

GOOGLE_SPLIT_SIZE = 100

def json_parse(file, key_list):
    with open(file, 'r') as f:
        json_list = json.load(f)
        return recursive_list_unpacker(json_list, key_list)

def json_translate(file, key_list, source_lang, target_lang):
    reference_list = []
    # Get the list of tags
    source_list = json_parse(file, key_list)
    for i, val in enumerate(source_list):
        if '\n' in val:
            print(val)
        source_list[i] = re.sub(r'$[\n]', '', val)
    # Translate the list of tags
    src_text_size = len(source_list)
    src_text_slice_count = src_text_size // GOOGLE_SPLIT_SIZE + 1
    for i in range(src_text_slice_count):
        start_pos = i * GOOGLE_SPLIT_SIZE
        end_pos = start_pos + GOOGLE_SPLIT_SIZE
        if end_pos > src_text_size:
            sub_list = source_list[start_pos:]
        else:
            sub_list = source_list[start_pos:end_pos]

        df = pd.DataFrame(sub_list)
        df = df.drop_duplicates()
        translated = google_translate('\n'.join(df[0].tolist()), source_lang, target_lang)
        translated_list = [translated[sentence] for sentence in sub_list]
        reference_list.extend(translated_list)

    return reference_list



def recursive_dict_unpacker(json_dict, key_list):
    output = []
    for i, value in json_dict.items():
        if i in key_list:
            output.append(json_dict.get(i))
        if isinstance(value, list):
            # If the value is a list then call the list fn
            for j in recursive_list_unpacker(value, key_list):
                output.append(j)

    return output


def recursive_list_unpacker(json_list, key_list):
    output = []
    # Go through the list looking for dictionaries
    for i in json_list:
        if isinstance(i, dict):
            # Call recursive dict fn
            for j in recursive_dict_unpacker(i, key_list):
                output.append(j)
    return output


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
    parser.add_argument(
        '--source_lang', default=['ko'],
        help='language to be translated from')
    parser.add_argument(
        '--target_lang', default=['en'],
        help='language to be translated to')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    text = json_translate(args.file, args.keys, args.source_lang, args.target_lang)
    # text = json_parse(args.file, args.keys)
    print(''.join(text))
