# TranslatorBot

A [GitHub Action](https://github.com/actions) for automatically translating the strings.xml file in your android project using Google Cloud Translate API.


## Features

* Parses the strings.xml file in the default values folder, translates strings if required using Translate API and creates
the respective localized strings.xml files.
* The bot will automatically add a commit to your branch/Pull Request if strings have been translated.
* Output languages can be configured on your workflow.

## Usage

This action has two required inputs.
1. An API key. If a non Leia repository, you can get your own cloud translations API key by following the instructions here.
2. The ISO-639-1 codes of the languages to translate to separated by a comma

For example, the following workflow adds the Translator action for every Pull request created to a project
The output languages are set to Spanish, French and Chinese.

You can look up the ISO-639-1 language codes specified [here](https://cloud.google.com/translate/docs/languages) .

```workflow
on: pull_request
name: Translations Workflow
jobs:
  formatCode:
    name: Translate Strings
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: '0'
      - name: translate strings
        uses: LeiaInc/TranslatorBot@v1.1
        with:
          translationKey: 'YOUR_API_KEY'
          outputLanguages: 'es,fr,zh'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

If using in a Leia repository, you can use the shared Translations API key
The following workflow uses the Shared translations key available for all Leia Repositories.
```workflow
on: pull_request
name: Translations Workflow
jobs:
  formatCode:
    name: Translate Strings
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: '0'
      - name: translate strings
        uses: LeiaInc/TranslatorBot@v1.1
        with:
          translationKey: ${{ secrets.GOOGLE_TRANSLATE_API_KEY }}
          outputLanguages: 'es,fr,zh'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
## Specification

- Bot will create a new localized strings.xml file if doesn't already exist, under
  app/src/main/res/values-*lang_code*/strings.xml
- If translations already exist, they will be copied over without translating even if the
  default strings.xml value is changed
- If translations exists and was written by the bot, the bot will update it everytime
  a change is made to the original strings.xml file.
- Non-translatable xml elements won't be copied over
