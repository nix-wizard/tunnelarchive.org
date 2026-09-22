#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../../lib.sh


enforce 'POST' "$REQUEST_METHOD"
enforce 'same-origin' "$HTTP_SEC_FETCH_SITE"

username="$REMOTE_USER"
cd "$db_path/users/by-username/$username"

declare -A body
parse_values "$(</dev/stdin)" body
assert_var "${body[bio]-}"
bio="${body[bio]-}"
enforce_length "$bio" '512'

printf '%s' "$bio" > bio

header 'Content-Type: text/html'
header ''

printf '%s\n' "$stylesheet"
printf '<p style="color: #00FF00">Success!</p>\n'
