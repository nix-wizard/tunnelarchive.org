#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh


enforce 'GET' "$REQUEST_METHOD"

declare -A queries
parse_values "${QUERY_STRING-}" queries
assert_var "${queries[username]-}"
username="${queries[username]-}"
check_username "$username"
if [ ! -d "$db_path/users/by-username/$username" ]; then
	return_status '404' "User \"$username\" does not exist."
fi
cd "$db_path/users/by-username/$username"

if [ ! -f './views' ]; then
	printf '0' > './views'
fi
views="$(<'./views')"
((views=views+1))
printf '%s' "$views" > "./views"

date="$(timestamp_to_date "$(<'./timestamp')")"

if [ ! -f './bio' ] || [ -z "$(<"./bio")" ]; then
	bio='This user has no bio.'
else
	bio="$(<'./bio')"
fi

if [ ! -f './homepage' ] || [ -z "$(<"./homepage")" ]; then
	homepage="/profile.cgi?username=$username"
else
	homepage="$(<'./homepage')"
fi

if [ ! -d './tunnels' ]; then
	tunnels='0'
else
	tunnels="$(<"./tunnels/count")"
fi

if [ ! -d './levels' ]; then
	levels='0'
else
	levels="$(<"./levels/count")"
fi

username="$(html_escape <<<"$username")"
date="$(html_escape <<<"$date")"
views="$(html_escape <<<"$views")"
homepage="$(html_escape <<<"$homepage")"
tunnels="$(html_escape <<<"$tunnels")"
levels="$(html_escape <<<"$levels")"
bio="$(html_escape <<<"$bio")"

homepage="$(generate_link "$homepage" "$homepage")"

content() {
	printf '%s' "$(<"$static_path/profile.html")" | \
		replace_all '<!-- USERNAME -->' "$username" | \
		replace_all '<!-- DATE -->' "$date" | \
		replace_all '<!-- VIEWS -->' "$views" | \
		replace_all '<!-- HOMEPAGE -->' "$homepage" | \
		replace_all '<!-- TUNNELS -->' "$tunnels" | \
		replace_all '<!-- LEVELS -->' "$levels" | \
		replace_all '<!-- BIO -->' "$bio"
}

title() {
	printf '%s' "$username"
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
