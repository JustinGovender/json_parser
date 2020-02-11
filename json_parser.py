import os
import sys
from shutil import copy2
import argparse
import json
import pandas as pd
from google_api import google_translate
import re
from collections import deque

GOOGLE_SPLIT_SIZE = 100


def json_parse(file, key_list):
    with open(file, 'r') as f:
        json_list = json.load(f)
        return recursive_list_unpacker(json_list, key_list)


def json_replace(file, key_list, target_lang, source_list, reference_list):
    # Duplicate original file
    new_filepath = os.path.join('.', os.path.basename(file) + '_' + target_lang)
    # Set up deque
    reference_deque = deque(reference_list)
    source_deque = deque(source_list)
    # Translate json dictionary
    with open(file, 'r') as f:
        json_list = json.load(f)
        recursive_list_unpacker(json_list, key_list, translate=True,
                                source_deque=source_deque, reference_deque=reference_deque)
    print('omg it worked?')
    # Dump to file
    with open(new_filepath, 'w', encoding='utf8') as fp:
        json.dump(json_list, fp, indent=2, ensure_ascii=False, )
    return



def json_translate(file, key_list, source_lang, target_lang):
    reference_list = []
    # Get the list of tags
    source_list = json_parse(file, key_list)
    for i, val in enumerate(source_list):
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
        # Google translate automatically skips duplicates so avoid sending
        df = pd.DataFrame(sub_list)
        df = df.drop_duplicates()
        translated = google_translate('\n'.join(df[0].tolist()), source_lang, target_lang)
        # Reconstruct matched list including duplicates
        translated_list = [translated[sentence] for sentence in sub_list]
        reference_list.extend(translated_list)

    # Now open
    json_replace(file, key_list, target_lang, source_list, reference_list)


def recursive_dict_unpacker(json_dict, key_list, translate=False, source_deque=None, reference_deque=None):
    output = []
    for i, value in json_dict.items():
        if i in key_list:
            if translate:
                json_dict[i] = reference_deque.popleft()
                source_deque.popleft()
            else:
                output.append(json_dict.get(i))
        if isinstance(value, list):
            # If the value is a list then call the list fn
            for j in recursive_list_unpacker(value, key_list, translate=translate,
                                             source_deque=source_deque, reference_deque=reference_deque):
                output.append(j)

    return output


def recursive_list_unpacker(json_list, key_list, translate=False, source_deque=None, reference_deque=None):
    output = []
    # Go through the list looking for dictionaries
    for i in json_list:
        if isinstance(i, dict):
            # Call recursive dict fn
            for j in recursive_dict_unpacker(i, key_list, translate=translate,
                                             source_deque=source_deque, reference_deque=reference_deque):
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
        '--source_lang', default='ko',
        help='language to be translated from')
    parser.add_argument(
        '--target_lang', default='en',
        help='language to be translated to')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    text = json_translate(args.file, args.keys, args.source_lang, args.target_lang)
    # text = json_parse(args.file, args.keys)
