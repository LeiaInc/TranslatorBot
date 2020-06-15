#!/bin/bash

_git_is_dirty() {
	[[ -n "$(git status -s)" ]]
}

_commit_and_push() {
	git add .
	git commit -m "translator-bot: Added Translations"
	git push
}

_commit_if_needed() {
	if _git_is_dirty; then
		_commit_and_push
	fi
}

_setup_git() {
  git config --global user.name "Translator-Bot"
  git config --global user.email "leia-codacy-bot@leiainc.com"

  git checkout "${GITHUB_BASE_REF}"
  git pull
  git checkout "${GITHUB_HEAD_REF}"
  git pull
}
