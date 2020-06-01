#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# output format: values-XX folders with strings.xml inside

# SUBROUTINES
# This subroutine reformats chinese strings to separate a 'd' or 's' character that is
# appended to the chinese character.
def parse_chinese_word(chinese_string):
    str_length = len(chinese_string)
    s = chinese_string
    for i, v in enumerate(chinese_string):
        if (v == 's') | (v == 'd') & (str_length > 1):
            splitPos = i + 1
            l,r = chinese_string[:splitPos], chinese_string[splitPos:]
            s = l+ " " +r
    return s

def reformat_chinese_string(chinese_string):
    words = chinese_string.split(' ')
    s = ""
    for singleWord in words:
        newWord = parse_chinese_word(singleWord)
        s+="" +newWord
    return s

# Function which calls the google translate API and converts the string to_translate to the language specified in to_language
def translate(to_translate, to_language="auto"):
    # send request
    to_translate = unescape(to_translate)
    to_translate = to_translate.replace('\\\'', '\'')
    to_translate = to_translate.replace('&', '%26')
    url = "https://translation.googleapis.com/language/translate/v2?source=en&target=%s&key=%s&q=%s"% (to_language, TRANSLATIONS_API_KEY, to_translate)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print ("Error occurred")
        return to_translate

    json_data = json.loads(response.text)
    translated_text = json_data['data']['translations'][0]['translatedText']
    if 'zh' in to_language :
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
    return parsed5

# function which handles nested xml tags like plural strings and string-arrays. Parses each
# child tag and calls the translate function.
def handle_nested_xml(root, i) :
    for j in range(len(root[i])):
        #   for each translatable string call the translation subroutine
        #   and replace the string by its translation,
        isTranslatable=root[i][j].get('translatable')
        if(root[i][j].tag=='item') & (isTranslatable!='false'):
            # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
            totranslate=root[i][j].text
            if(totranslate!=None):
                root[i][j].text=translate(totranslate,OUTPUT_LANGUAGE).replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

            # if string was broken down due to HTML tags, reassemble it
            if len(root[i][j]) != 0:
                for element in range(len(root[i][j])):
                    root[i][j][element].text = " " + translate(root[i][j][element].text, OUTPUT_LANGUAGE).replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')
                    root[i][j][element].tail = " " + translate(root[i][j][element].tail, OUTPUT_LANGUAGE).replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

# MAIN PROGRAM
# import libraries
import requests
from requests.exceptions import HTTPError
from html import unescape
import os
import xml.etree.ElementTree as ET
import json
import re
import sys

TRANSLATIONS_API_KEY = sys.argv[1]
OUTPUT_LANGUAGES = sys.argv[2]
OUTPUT_LANGUAGE_LIST = OUTPUT_LANGUAGES.split(',')
print (OUTPUT_LANGUAGE_LIST)
BASEPATH = "app/src/main/res/"
INFILE = BASEPATH + "values/" + "strings.xml"
INPUTLANGUAGE = "en"

for OUTPUT_LANGUAGE in OUTPUT_LANGUAGE_LIST:
    # create outfile in subfolder if doesn't already exist
    name, ext=os.path.splitext(INFILE)
    if not os.path.exists(BASEPATH + "values-" + OUTPUT_LANGUAGE):
        os.mkdir(BASEPATH + "values-" + OUTPUT_LANGUAGE)
    OUTFILE = BASEPATH + "values-" + OUTPUT_LANGUAGE + "/strings.xml"

    # read xml structure
    tree = ET.parse(INFILE)
    root = tree.getroot()
    # Keeps track of xml elements marked as non-translatable
    removal_list = []

    # cycle through elements
    for i in range(len(root)):
        #	for each translatable string call the translation subroutine
        #   and replace the string by its translation,
        #   descend into each string array
        isTranslatable=root[i].get('translatable')
        if(root[i].tag=='string') & (isTranslatable!='false'):
            # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
            totranslate=root[i].text
            if(totranslate!=None):
                root[i].text=translate(totranslate,OUTPUT_LANGUAGE).replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

            # if string was broken down due to HTML tags, reassemble it
            if len(root[i]) != 0:
                for element in range(len(root[i])):
                    root[i][element].text = " " + translate(root[i][element].text, OUTPUT_LANGUAGE).replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')
                    root[i][element].tail = " " + translate(root[i][element].tail, OUTPUT_LANGUAGE).replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

        if(root[i].tag=='string-array'):
            handle_nested_xml(root, i)

        if(root[i].tag=='plurals'):
            handle_nested_xml(root, i)

        if isTranslatable == 'false':
            # Add to the removal_list
            removal_list.append(root[i])

    # Remove elements marked as non-translatable
    for element in removal_list:
        root.remove(element)

    # write new xml file
    tree.write(OUTFILE, encoding='utf-8')
