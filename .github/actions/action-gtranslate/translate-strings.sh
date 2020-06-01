#!/usr/bin/env bash

set -e

# shellcheck disable=SC1091
source /lib.sh

_setup_git
echo $1
echo $2
echo ${INPUT_TRANSLATIONKEY}
echo ${INPUT_OUTPUTLANGUAGES}

if _should_translate;then
  _copy_scripts
  python3 gtranslate.py $1 $2
  _remove_scripts
  _requires_token
  _commit_if_needed
  fi

