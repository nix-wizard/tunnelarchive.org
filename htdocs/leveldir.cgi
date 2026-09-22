#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh


enforce 'GET' "$REQUEST_METHOD"
mkdir -p "$db_path/levels"
cd "$db_path/levels"

declare -A queries
parse_values "${QUERY_STRING-}" queries
username="${queries[username]-}"
if [ "$username" ]; then
	check_username "$username"
fi

levels() {
	local leveldirs=(./by-timestamp/*/)
	local levelid
	local author
	local name
	local difficulty
	local game
	local date
	local level
	for ((i=${#leveldirs[@]}-1; i>=0; i--)); do
		author="$(<"${leveldirs[$i]}/author/username")"
		if [ "$username" ] && [ "$username" != "$author" ]; then
			continue
		fi
		author="$(generate_link "$author" "/profile.cgi?username=$author")"
		author="$(generate_tag 'td' "$author")"
		
		levelid="$(<"${leveldirs[$i]}/levelid")"

		name="$(<"${leveldirs[$i]}/name")"
		name="$(html_escape <<<"$name")"
		name="$(generate_link "$name" "/level.cgi?levelid=$levelid")"
		name="$(generate_tag 'td' "$name")"

		levelid="$(generate_tag 'td' "$levelid")"

		difficulty="$(<"${leveldirs[$i]}/difficulty")"
		difficulty="$(generate_tag 'td' "$difficulty")"

		game="$(<"${leveldirs[$i]}/game")"
		game="$(game_to_string "$game")"
		game="$(generate_tag 'td' "$game")"
		
		date="$(timestamp_to_date "$(<"${leveldirs[$i]}/timestamp")")"
		date="$(generate_tag 'td' "$date")"
		

		level="$name $levelid $difficulty $game $date $author"
		level="$(generate_tag 'tr' "$level")"
		printf '%s' "$level"
	done
}

content() {
	levels="$(levels)"
	printf '%s' "$(<"$static_path/leveldir.html")" | \
		replace_all '<!-- LEVELS -->' "$levels"
}

title() {
	printf 'level directory'
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
