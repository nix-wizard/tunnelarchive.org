#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../lib.sh


enforce 'GET' "$REQUEST_METHOD"

username="$REMOTE_USER"
cd "$db_path/users/by-username/$username"

if [ ! -f './bio' ] || [ -z "$(<"./bio")" ]; then
	bio=''
else
	bio="$(<'./bio')"
fi

if [ ! -f './homepage' ] || [ -z "$(<"./homepage")" ]; then
	homepage=''
else
	homepage="$(<'./homepage')"
fi

username="$(html_escape <<<"$username")"
homepage="$(html_escape <<<"$homepage")"
bio="$(html_escape <<<"$bio")"

content() {
	printf '%s' "$(<"$static_path/user/edit-profile.html")" | \
		replace_all '<!-- USERNAME -->' "$username" | \
		replace_all '<!-- HOMEPAGE -->' "$homepage" | \
		replace_all '<!-- BIO -->' "$bio"
}

title() {
	printf '%s' "editing $username"
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
