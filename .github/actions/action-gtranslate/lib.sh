#!/bin/bash

# This file adapted from https://github.com/bltavares/actions/blob/master/prettier/lib.sh

_is_automated_event() {
	AUTOFIX_EVENTS=${AUTOFIX_EVENTS:-push}

	if [[ ${GITHUB_EVENT_NAME} =~ ^($AUTOFIX_EVENTS)$ ]]; then
		return 0
	fi

	return 1
}

_requires_token() {
	if [[ -z $GITHUB_TOKEN ]]; then
		echo "Set the GITHUB_TOKEN env variable."
		exit 1
	fi
}

_git_is_dirty() {
	[[ -n "$(git status -s)" ]]
}

_commit_and_push() {
	git add app/src/main/res/*
	git commit -m "translator-bot: Added Translations"
	git pull
	git push
}

_commit_if_needed() {
	if _git_is_dirty; then
		_commit_and_push
	fi
}

_should_translate() {
  stringsFile="app/src/main/res/values/strings.xml"
  for i in $(git diff ${GITHUB_HEAD_REF} ${GITHUB_BASE_REF} --name-only); do
    if [ "$i" == "$stringsFile" ]
    then
      return 0
      fi
  done
  return 1
}

_remove_scripts() {
  rm gtranslate.py translation-config.properties
}

_setup_git() {
  git config --global user.name "Translator-Bot"
  git config --global user.email "leia-codacy-bot@leiainc.com"

  git checkout "${GITHUB_BASE_REF}"
  git pull
  git checkout "${GITHUB_HEAD_REF}"
  git pull
}

_copy_scripts() {
  cd /
  cp gtranslate.py "${GITHUB_WORKSPACE}"
  cp translation-config.properties "${GITHUB_WORKSPACE}"
  cd "${GITHUB_WORKSPACE}"
}
