#!/bin/sh
# bash script to commit in accordance with the branch name
# usage: ./scripts/commit.sh
branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
branch="${branch##*feature/}"
branch="${branch//\_/ }"
git commit -m "$branch"