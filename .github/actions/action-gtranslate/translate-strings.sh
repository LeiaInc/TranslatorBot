#!/usr/bin/env bash

set -e

# shellcheck disable=SC1091
source /lib.sh

_setup_git

if _should_translate;then
  _copy_scripts
  python3 gtranslate.py ${INPUT_TRANSLATION-API-KEY} ${INPUT_OUTPUT-LANGUAGES}
  _remove_scripts
  _requires_token
  _commit_if_needed
  fi

