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


def json_parse(file, tag_list):
    """
    Gets the contents from tags specified by the tag list from a json file.
    :param file: The json file to be parsed
    :param tag_list: The list of tags whose content will be returned
    :return: returns a list containing contents of the specified tags
    """
    with open(file, 'r') as f:
        json_list = json.load(f)
        return recursive_list_unpacker(json_list, tag_list)


def json_replace(file, key_list, target_lang, indent, reference_dict):
    # Duplicate original file
    new_filepath = os.path.join('.', os.path.splitext((os.path.basename(file)))[0] + '_' + target_lang + '.json')
    # Translate json dictionary
    with open(file, 'r') as f:
        json_list = json.load(f)
        recursive_list_unpacker(json_list, key_list, translate=True, references=reference_dict)
    # Dump to file
    with open(new_filepath, 'w', encoding='utf8') as fp:
        json.dump(json_list, fp, indent=indent, ensure_ascii=False, )
    return


def json_translate(file, tag_list, source_lang, target_lang, indent):
    """
    Creates a new json file with the contents from the specified tags translated into the target language.
    :param file: The json file to be translated.
    :param tag_list: The list of tags whose content will be translated.
    :param source_lang: The language to be translated from.
    :param target_lang: The language to be translated to.
    :param indent: Amount of spaces the translated json file will be indented by.
    :return: Creates a translated file but does not return anything.
    """
    reference_dict = {}
    # Get the list of tags
    source_list = json_parse(file, tag_list)
    # Preserve special characters by replacing them with unique tags
    for i, val in enumerate(source_list):
        val = val.replace('\n', '<gconnl>')
        val = val.replace('  ', '<gconspace>')
        val = val.replace('\t', '<gcontab>')
        source_list[i] = val

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

    # Put special characters back
    new_dict = {}
    for key in reference_dict.keys():
        if any(word in key for word in ['<gconnl>', '<gconspace>']):
            # Create new entry with correct values
            new_key = key.replace('<gconnl>', '\n')
            new_key = new_key.replace('<gconspace>', '  ')
            new_key = new_key.replace('<gcontab>', '\t')
            new_value = reference_dict[key].replace('<gconnl>', '\n')
            new_value = new_value.replace('<gconspace>', '  ')
            new_value = new_value.replace('<gcontab>', '\t')

            new_dict[new_key] = new_value
        else:
            new_dict[key] = reference_dict[key]
    # Create new translated file
    json_replace(file, tag_list, target_lang, indent, reference_dict=new_dict)


def parse_args(argv):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='json_parser_args')
    # set the argument formats
    parser.add_argument(
        '--file', default=os.path.join('.', 'json_files', 'backup.json'),
        help='json file to be parsed')
    parser.add_argument(
        '--tags',
        default=['text', 'title', 'desc'],
        help='json file keys to be searched for')
    parser.add_argument(
        '--source_lang', default='ko',
        help='language to be translated from')
    parser.add_argument(
        '--target_lang', default='en',
        help='language to be translated to')
    parser.add_argument(
        '--json_indent', default=4,
        help='number of spaces the translated json file should be indented')

    return parser.parse_args(argv[1:])


if __name__ == '__main__':
    args = parse_args(sys.argv)
    json_translate(args.file, args.tags, args.source_lang, args.target_lang, args.json_indent)
