#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh


enforce 'GET' "$REQUEST_METHOD"
mkdir -p "$db_path/tunnels"
cd "$db_path/tunnels"

declare -A queries
parse_values "${QUERY_STRING-}" queries
username="${queries[username]-}"
if [ "$username" ]; then
	check_username "$username"
fi

tunnels() {
	local tunneldirs=(./by-timestamp/*/)
	local tunnelid
	local author
	local name
	local difficulty
	local game
	local count
	local date
	local tunnel
	for ((i=${#tunneldirs[@]}-1; i>=0; i--)); do
		author="$(<"${tunneldirs[$i]}/author/username")"
		if [ "$username" ] && [ "$username" != "$author" ]; then
			continue
		fi
		author="$(generate_link "$author" "/profile.cgi?username=$author")"
		author="$(generate_tag 'td' "$author")"
		
		tunnelid="$(<"${tunneldirs[$i]}/tunnelid")"

		name="$(<"${tunneldirs[$i]}/name")"
		name="$(html_escape <<<"$name")"
		name="$(generate_link "$name" "/tunnel.cgi?tunnelid=$tunnelid")"
		name="$(generate_tag 'td' "$name")"

		tunnelid="$(generate_tag 'td' "$tunnelid")"

		difficulty="$(<"${tunneldirs[$i]}/difficulty")"
		difficulty="$(generate_tag 'td' "$difficulty")"

		game="$(<"${tunneldirs[$i]}/game")"
		game="$(game_to_string "$game")"
		game="$(generate_tag 'td' "$game")"

		count="$(<"${tunneldirs[$i]}/count")"
		count="$(generate_tag 'td' "$count")"
		
		date="$(timestamp_to_date "$(<"${tunneldirs[$i]}/timestamp")")"
		date="$(generate_tag 'td' "$date")"

		tunnel="$name $tunnelid $difficulty $game $count $date $author"
		tunnel="$(generate_tag 'tr' "$tunnel")"
		printf '%s' "$tunnel"
	done
}

content() {
	tunnels="$(tunnels)"
	printf '%s' "$(<"$static_path/tunneldir.html")" | \
		replace_all '<!-- TUNNELS -->' "$tunnels"
}

title() {
	printf 'tunnel directory'
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
