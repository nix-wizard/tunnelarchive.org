#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh


enforce 'GET' "$REQUEST_METHOD"

declare -A queries
parse_values "${QUERY_STRING-}" queries
assert_var "${queries[levelid]-}"
levelid="${queries[levelid]-}"
enforce_length "$levelid" 8
enforce_number "$levelid"
if [ ! -d "$db_path/levels/by-levelid/$levelid" ]; then
	return_status '404' "Levelid \"$levelid\" does not exist."
fi
cd "$db_path/levels/by-levelid/$levelid"

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
data="$(<'./data')"
difficulty="$(<'./difficulty')"
attribution="$(<'./attribution')"

name="$(html_escape <<<"$name")"
description="$(html_escape <<<"$description")"
data="$(html_escape <<<"$data")"
difficulty="$(html_escape <<<"$difficulty")"
attribution="$(html_escape <<<"$attribution")"

if [ -z "$attribution" ]; then
	attribution='None'
else
	attribution="$(generate_link "$attribution" "/level.cgi?levelid=$attribution")"
fi

if [ -z "$description" ]; then
	description='This level has no description.'
fi

tunnels() {
	local name
	local tunnelid
	local author
	local entry
	for tunnel in ./tunnels/*/; do
		tunnelid="$(<"$tunnel/tunnelid")"

		name="$(<"$tunnel/name")"
		name="$(html_escape <<<"$name")"
		name="$(generate_link "$name" "/tunnel.cgi?tunnelid=$tunnelid")"

		author="$(<"$tunnel/author/username")"
		author="$(generate_link "$author" "/profile.cgi?username=$author")"

		entry="$name by $author"
		entry="$(generate_tag 'li' "$entry")"
	done
	entry="$(generate_tag 'ul' "$entry")"
	printf '%s ' "$entry"
}
if [ -d ./tunnels ] && [ "$(ls ./tunnels)" ]; then
	tunnels="$(tunnels)"
else
	tunnels='None.'
	tunnels="$(generate_tag 'p' "$tunnels")"
fi

content() {
	printf '%s' "$(<"$static_path/level.html")" | \
		replace_all '<!-- LEVELID -->' "$levelid" | \
		replace_all '<!-- AUTHOR -->' "$author" | \
		replace_all '<!-- DATE -->' "$date" | \
		replace_all '<!-- VIEWS -->' "$views" | \
		replace_all '<!-- NAME -->' "$name" | \
		replace_all '<!-- DESCRIPTION -->' "$description" | \
		replace_all '<!-- DATA -->' "$data" | \
		replace_all '<!-- DIFFICULTY -->' "$difficulty" | \
		replace_all '<!-- ATTRIBUTION -->' "$attribution" | \
		replace_all '<!-- TUNNELS -->' "$tunnels" 
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
