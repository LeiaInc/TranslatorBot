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
  git config --global user.name "leiapixadmins"
  git config --global user.email "leiapixadmins@leiainc.com"
  git remote set-url origin git@github.com:LeiaInc/TranslatorBot.git

  git checkout "${GITHUB_BASE_REF}"
  git pull
  git checkout "${GITHUB_HEAD_REF}"
  git pull
}
