#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh


enforce 'GET' "$REQUEST_METHOD"

content() {
	printf '%s' "$(<"$static_path/register.html")"
}

title() {
	printf 'register'
}

page() {
	printf '%s' "$REQUEST_URI"
}

content="$(content)"
title="$(title)"
page="$(page)"

header 'Content-Type: text/html'
header ''

generate_page "$content" "$title" "$page"
