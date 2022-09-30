#!/bin/sh
# bash script to create a new branch that respects the library standard
# usage: ./scripts/create_new_branch.sh "[FEAT] - Implement instrument types #14"
issue=$1
issue_number=${issue##*#}
issue="${issue%%#*}"
issue="${issue//\[FEAT\] \- /}"
issue="${issue// /\_}"
issue=${issue::-1}
branch_name="feature/Issue-$issue_number $issue"
branch_name="${branch_name// /\_}"
git checkout -b $branch_name


