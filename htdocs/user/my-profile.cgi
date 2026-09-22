#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../lib.sh


enforce 'GET' "$REQUEST_METHOD"

username="$REMOTE_USER"

header 'Content-Type: text/html'
header 'Status: 301'
header "Location: /profile.cgi?username=$username"
header ''

generate_tag 'p' 'Redirecting...'
