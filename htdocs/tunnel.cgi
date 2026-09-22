#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh

enforce 'GET' "$REQUEST_METHOD"

declare -A queries
parse_values "${QUERY_STRING-}" queries
assert_var "${queries[tunnelid]-}"
tunnelid="${queries[tunnelid]-}"
enforce_length "$tunnelid" 8
enforce_number "$tunnelid"
if [ ! -d "$db_path/tunnels/by-tunnelid/$tunnelid" ]; then
	return_status '404' "Tunnelid \"$tunnelid\" does not exist."
fi
cd "$db_path/tunnels/by-tunnelid/$tunnelid"

if [ ! -f './views' ]; then
	printf '0' > './views'
fi
views="$(<'./views')"
((views=views+1))
printf '%s' "$views" > "./views"

date="$(timestamp_to_date "$(<'./timestamp')")"

author="$(<"./author/username")"
name="$(<'./name')"
description="$(<'./description')"
difficulty="$(<'./difficulty')"

name="$(html_escape <<<"$name")"
description="$(html_escape <<<"$description")"
difficulty="$(html_escape <<<"$difficulty")"

if [ -z "$description" ]; then
	description='This level has no description.'
fi

levels() {
	local name
	local levelid
	local author
	local entry
	for level in ./levels/*/; do
		levelid="$(<"$level/levelid")"

		name="$(<"$level/name")"
		name="$(html_escape <<<"$name")"
		name="$(generate_link "$name" "/level.cgi?levelid=$levelid")"

		author="$(<"$level/author/username")"
		author="$(generate_link "$author" "/profile.cgi?username=$author")"

		entry="$name by $author"
		entry="$(generate_tag 'li' "$entry")"
		printf '%s ' "$entry"
	done
}
levels="$(levels)"

levelauthors() {
	local username
	for levelauthor in ./levelauthors/*/; do
		username="$(<"$levelauthor/username")"
		username="$(generate_link "$username" "/profile.cgi?username=$username")"
		printf '%s' "$username"
	done
}
levelauthors="$(levelauthors)"

content() {
	printf '%s' "$(<"$static_path/tunnel.html")" | \
		replace_all '<!-- TUNNELID -->' "$tunnelid" | \
		replace_all '<!-- AUTHOR -->' "$author" | \
		replace_all '<!-- LEVELAUTHORS -->' "$levelauthors" | \
		replace_all '<!-- DATE -->' "$date" | \
		replace_all '<!-- VIEWS -->' "$views" | \
		replace_all '<!-- NAME -->' "$name" | \
		replace_all '<!-- DESCRIPTION -->' "$description" | \
		replace_all '<!-- LEVELS -->' "$levels" | \
		replace_all '<!-- DIFFICULTY -->' "$difficulty"
}

title() {
	printf '%s' "$name"
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
