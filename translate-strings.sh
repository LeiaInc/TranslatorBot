#!/usr/bin/env bash

set -e

# shellcheck disable=SC1091
source /lib.sh

_setup_git
python3 /gtranslate.py ${INPUT_TRANSLATIONKEY} ${INPUT_OUTPUTLANGUAGES} ${GITHUB_WORKSPACE}
_commit_if_needed


