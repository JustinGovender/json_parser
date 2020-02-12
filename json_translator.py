import os
import sys
import argparse
import json
import pandas as pd
from google_api import google_translate


GOOGLE_SPLIT_SIZE = 100


def recursive_dict_unpacker(json_dict, key_list, translate=False, references=None):
    output = []
    for i, value in json_dict.items():
        if i in key_list:
            if translate:
                json_dict[i] = references[value]
            else:
                output.append(json_dict.get(i))
        if isinstance(value, list):
            # If the value is a list then call the list fn
            for j in recursive_list_unpacker(value, key_list, translate=translate, references=references):
                output.append(j)

    return output


def recursive_list_unpacker(json_list, key_list, translate=False, references=None):
    output = []
    # Go through the list looking for dictionaries
    for i in json_list:
        if isinstance(i, dict):
            # Call recursive dict fn
            for j in recursive_dict_unpacker(i, key_list, translate=translate, references=references):
                output.append(j)
    return output


def json_parse(file, key_list):
    with open(file, 'r') as f:
        json_list = json.load(f)
        return recursive_list_unpacker(json_list, key_list)


def json_replace(file, key_list, target_lang, reference_dict):
    # Duplicate original file
    new_filepath = os.path.join('.', os.path.splitext((os.path.basename(file)))[0] + '_' + target_lang + '.json')
    # Translate json dictionary
    with open(file, 'r') as f:
        json_list = json.load(f)
        recursive_list_unpacker(json_list, key_list, translate=True, references=reference_dict)
    # Dump to file
    with open(new_filepath, 'w', encoding='utf8') as fp:
        json.dump(json_list, fp, indent=2, ensure_ascii=False, )
    return


def json_translate(file, key_list, source_lang, target_lang):
    reference_dict = {}
    # Get the list of tags
    source_list = json_parse(file, key_list)
    # google_api.py will split any line that has a \n character so change them to a special sequence
    for i, val in enumerate(source_list):
        source_list[i] = val.replace('\n', '<gconnl>')
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
        reference_dict.update(translated)

    # Put newlines back in
    for key, value in reference_dict.items():
        if '<gconnl>' in key:
            # Create new entry with correct values
            reference_dict[key.replace('<gconnl>', '\n')] = value.replace('<gconnl>', '\n')
            # Remove old key
            del reference_dict[key]
    # Create new translated file
    json_replace(file, key_list, target_lang, reference_dict=reference_dict)


def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='json_parser_args')
    # set the argument formats
    parser.add_argument(
        '--file', default=os.path.join('.', 'json_files', 'kubernetes.json'),
        help='json file to be parsed')
    parser.add_argument(
        '--keys',
        default=['text', 'title'],
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
    json_translate(args.file, args.keys, args.source_lang, args.target_lang)