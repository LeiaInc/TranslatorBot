import translator_bot
import os

"""
This script is invoked from translate-strings.sh, which is intended to be run as part of a Github Action.

If you want to run the tool on the command line, use translator_bot.py instead.
"""


def show_required_field_error(required_field: str):
    print('%s is a required field.' % required_field)
    print('Please confirm your Workflow YML is set up as described at https://github.com/LeiaInc/TranslatorBot#usage.')


if __name__ == "__main__":
    api_key = os.getenv('INPUT_TRANSLATIONKEY')
    if not api_key:
        show_required_field_error('translationKey')
        exit()

    output_languages = os.getenv('INPUT_OUTPUTLANGUAGES')
    if not output_languages:
        show_required_field_error('outputLanguages')
        exit()

    res_directories = os.getenv('INPUT_RESDIRECTORIES')
    if not res_directories:
        show_required_field_error('resDirectories')
        exit()

    output_language_list = output_languages.split(',')

    for res_dir in res_directories.split(','):
        translator_bot.translate_res_dir(api_key, output_language_list, res_dir)
