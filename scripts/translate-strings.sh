#!/usr/bin/env bash

set -e

# shellcheck disable=SC1091
source /scripts/lib.sh

#_setup_git
python3 /scripts/auto_translate_from_github_action.py
#_commit_if_needed


