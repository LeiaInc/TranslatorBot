#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# output format: values-XX folders with strings.xml inside


def parse_chinese_word(chinese_string):
    str_length = len(chinese_string)
    formatted_string = chinese_string
    for i, v in enumerate(chinese_string):
        if (v == 's') or (v == 'd') and (str_length > 1):
            split_pos = i + 1
            l, r = chinese_string[:split_pos], chinese_string[split_pos:]
            formatted_string = l + " " + r
    return formatted_string


def reformat_chinese_string(chinese_string):
    words = chinese_string.split(' ')
    formatted_string = ""
    for singleWord in words:
        new_word = parse_chinese_word(singleWord)
        formatted_string += "" + new_word
    return formatted_string


def query_translations_api(text_to_translate, to_language):

    params = {'source': 'en', 'target': to_language, 'key': TRANSLATIONS_API_KEY, 'q': text_to_translate }
    # Edge case where Google doesn't translate correctly if there is a period immediately before \n. Add a space

    url = "https://translation.googleapis.com/language/translate/v2?%s" % (urllib.parse.urlencode(params))
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        status_code = http_err.response.status_code
        print("Http Error occurred - Error Status Code : " + status_code)
        exit(1)

    json_data = json.loads(response.text)
    translated_text = json_data['data']['translations'][0]['translatedText']
    translated_text = translated_text.replace('0x0A', '\\n')
    return translated_text


# Function which calls the google translate API and converts the string to_
# translate to the language specified in to_language
def translate(text_to_translate, to_language="auto"):
    # Workaround for issue with google translate translating \n to \norde
    text_to_translate = text_to_translate.replace('.\\n', '. \\n')
    text_to_translate = text_to_translate.replace('\\n', '0x0A')
    print('Translating to ' + to_language + ' - ' + text_to_translate)
    translated_text = query_translations_api(text_to_translate, to_language)

    if 'zh' in to_language:
        # There's an issue with placeholder strings i.e Strings with %1$s, %1$d, %d, %s getting
        # misaligned in the response. This occurs only for chinese translations. Reformat the string
        # in that case
        translated_text = reformat_chinese_string(translated_text)
        translated_text = translated_text.replace('％', '%')

    parsed2 = unescape(translated_text)
    # fix parameter strings
    parsed3 = re.sub('% ([ds])', r' %\1', parsed2)
    parsed4 = re.sub('% ([\d]) \$ ([ds])', r' %\1$\2', parsed3).strip()
    parsed5 = parsed4.replace('\'', '\\\'')
    parsed6 = parsed5.replace('0x0A', '\\n')
    return parsed6


# Handles parsing a single xml tag. (<string> for regular string xml or <item> for plural, string-arrays)
# and calling the translate function. Translates the xml only if
#  1) translated strings.xml doesn't exist
#  2) translated element doesn't exist in the translated strings.xml file
#  3) Existing translated element has been changed since the last translation.
#
# If one of the above conditions are satisfied, the translate function is called to translate the english
# string and save the hash of the existing english text in the 'translated-from' attribute for that
# xml.
#
# If conditions are not satisfied, it simply copies over the existing translated element from the existing
# translated strings.xml into the current element.

# Also handles, single xml elements that are further broken down by Element tree because of
# html tags used within the xml text.
def handle_single_xml_element_translation(existing_xml_element, single_xml_element, output_language):

    if (len(single_xml_element) == 0) and (single_xml_element.text is not None):
        # Simple xml with text
        text_to_translate = single_xml_element.text
        existing_text_hashcode = ""
        manual_translation_exists = False
        if existing_xml_element is not None:
            # Get hashcode of previously translated english string if exists
            existing_text_hashcode = existing_xml_element.get('translated-from')
            manual_translation_exists = existing_text_hashcode is None

        if should_translate(existing_text_hashcode, text_to_translate, manual_translation_exists):
            # Contents are not same. Translate the text in the xml
            single_xml_element.text = translate(text_to_translate, output_language).replace('\\ ', '\\') \
                .replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')
            single_xml_element.set('translated-from', encode(text_to_translate))
        else:
            # Contents are same. Copy over the existing translated xml text into the current xml
            single_xml_element.text = existing_xml_element.text
            if not manual_translation_exists:
                single_xml_element.set('translated-from', existing_xml_element.get('translated-from'))

    elif len(single_xml_element) > 0:
        # XML was broken down due to nested html tags in the text. Reassemble the text by removing
        # the html tags.
        nested_text = get_nested_xml_text(single_xml_element)
        existing_text_hashcode = ""
        manual_translation_exists = False
        if existing_xml_element is not None:
            # Get hashcode of previously translated english string if exists
            existing_text_hashcode = existing_xml_element.get('translated-from')
            manual_translation_exists = existing_text_hashcode is None

        if should_translate(existing_text_hashcode, nested_text, manual_translation_exists):
            # String was changed. Extract the string from html, translate it and reassemble.
            reassembled_string = ""
            if single_xml_element.text is not None:
                reassembled_string += single_xml_element.text
                single_xml_element.text = translate(single_xml_element.text, output_language)
            # if string was broken down due to HTML tags, reassemble it
            for child_element in single_xml_element:
                if child_element.text is not None:
                    reassembled_string += child_element.text
                    # print('Text is ' + child_element.text)
                    child_element.text = " " + translate(child_element.text, output_language).replace('\\ ', '\\') \
                        .replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

                if child_element.tail is not None:
                    # print('Tail is ' + child_element.tail)
                    reassembled_string += child_element.tail
                    child_element.tail = " " + translate(child_element.tail, output_language).replace('\\ ', '\\') \
                        .replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

                # print('Complete text is ' + s)
                # Use the reassembled english string to encode the hash and save it in the 'translated-from' attribute
                single_xml_element.set('translated-from', encode(reassembled_string))
        else:
            # Contents of existing xml element is the same. Simply copy it over with the nested html.
            single_xml_element.text = existing_xml_element.text
            for child_element, existing_child_element in zip(single_xml_element, existing_xml_element):
                child_element.text = existing_child_element.text
                child_element.tail = existing_child_element.tail

            if not manual_translation_exists:
                single_xml_element.set('translated-from', existing_xml_element.get('translated-from'))


# Returns hash of a string
def encode(text):
    result = hashlib.md5(text.encode())
    h = result.hexdigest()

    # Truncate the hash for readability of the generated files.
    # An entropy of 16^8 means less than a one in 4 billion chance of any 2 strings having a hash collision.
    return h[:8]


# Finds and returns xml element if exists in the given root.
def get_existing_xml(existing_root, element_to_find):
    if existing_root is None:
        return None
    xml_search_query = ".//%s[@name='%s']" % (element_to_find.tag, element_to_find.get('name'))
    return existing_root.find(xml_search_query)


# Assembles text that was broken down in an xml element due to html tags
# present within the text.
def get_nested_xml_text(nested_xml_element):
    s = ""
    if (nested_xml_element is not None) and (nested_xml_element.text is not None):
        s += nested_xml_element.text
    for child_xml in nested_xml_element:
        if child_xml.text is not None:
            s += child_xml.text
        if child_xml.tail is not None:
            s += child_xml.tail
    return s


# Returns true if the hashcode of text_to_translate is the same as
# the existing_xml_hashcode
def should_translate(existing_xml_hashcode, text_to_translate, translation_exists):
    if translation_exists:
        return False
    if (existing_xml_hashcode is not None) and (text_to_translate is not None):
        current_text_hashcode = encode(text_to_translate)
        # print(existing_element_text)
        # print(current_text_hashcode)
        if existing_xml_hashcode == current_text_hashcode:
            return False
    return True


def translate_res_dir(language_codes, res_dir: str):

    infile = res_dir + "/values/" + "strings.xml"

    for output_language in language_codes:
        # create outfile in subfolder if doesn't already exist
        if not os.path.exists(res_dir + "/values-" + output_language):
            os.mkdir(res_dir + "/values-" + output_language)
        out_file = res_dir + "/values-" + output_language + "/strings.xml"

        existing_translated_tree = None
        existing_translated_root = None

        if os.path.exists(out_file):
            # If translated strings.xml exists, parse it and get the root.
            existing_translated_tree = ET.parse(out_file)
            existing_translated_root = existing_translated_tree.getroot()

        # read xml structure
        english_tree = ET.parse(infile)
        english_root = english_tree.getroot()
        removal_list = []

        # cycle through xml elements in english strings.xml
        for xml_element in english_root.iter():

            is_translatable = xml_element.get('translatable')

            if is_translatable == 'false':
                # is_translatable attribute is set to false. Simply continue.
                removal_list.append(xml_element)
                continue

            # Beyond this point, all strings are translatable.

            if xml_element.tag == 'string':
                # XML element is of type <string></string>
                existing_translated_xml_element = get_existing_xml(existing_translated_root, xml_element)
                handle_single_xml_element_translation(existing_translated_xml_element, xml_element, output_language)

            elif (xml_element.tag == 'string-array') or (xml_element.tag == 'plurals'):
                # XML element is of type <string-array></string-array> or <plurals>
                existing_translated_xml_element = get_existing_xml(existing_translated_root, xml_element)
                if (existing_translated_xml_element is not None) \
                        and (len(existing_translated_xml_element) == len(xml_element)):
                    # This xml element exists in translated file, cycle through both, and translate
                    for existing_item_element, item_element in zip(existing_translated_xml_element, xml_element):
                        handle_single_xml_element_translation(existing_item_element, item_element, output_language)
                else:
                    # This xml element doesn't exist, simply translate.
                    for item_element in xml_element:
                        handle_single_xml_element_translation(None, item_element, output_language)

        for element in removal_list:
            english_root.remove(element)

        # write the translated tree to the output file.
        english_tree.write(out_file, encoding="utf-8")


if __name__ == '__main__':

    # import libraries
    import requests
    from requests.exceptions import HTTPError
    from html import unescape
    import os
    import xml.etree.ElementTree as ET
    import json
    import re
    import hashlib
    import argparse
    import urllib.parse

    parser = argparse.ArgumentParser()
    parser.add_argument('api_key', action='store', type=str, help='The API key for Google Translate API')
    parser.add_argument('output_languages', action='store', type=str,
                        help='Output languages separated by comma. For eg. '
                             'To translate to spanish and french, use \'es,fr\'')
    parser.add_argument('res_dirs', type=str,
                        help='A list of 1 or more Android res dirs to translate'
                             '(ie, "app/src/main/res/,lib/src/main/res/")')
    args = parser.parse_args()

    TRANSLATIONS_API_KEY = args.api_key
    OUTPUT_LANGUAGES = args.output_languages

    OUTPUT_LANGUAGE_LIST = OUTPUT_LANGUAGES.split(',')

    for res_dir in args.res_dirs.split(','):
        translate_res_dir(OUTPUT_LANGUAGE_LIST, res_dir)

