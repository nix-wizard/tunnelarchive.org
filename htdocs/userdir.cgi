#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../lib.sh


enforce 'GET' "$REQUEST_METHOD"
mkdir -p './users'
cd "$db_path/users"

users() {
	userdirs=(./by-username/*/)
	local username
	local tunnels
	local levels
	local date
	local user
	for ((i=${#userdirs[@]}-1; i>=0; i--)); do
		username="$(<"${userdirs[$i]}/username")"
		username="$(generate_link "$username" "/profile.cgi?username=$username")"
		username="$(generate_tag 'td' "$username")"

		if [ ! -d "${userdirs[$i]}/tunnels" ]; then
			tunnels='0'
		else
			tunnels="$(<"${userdirs[$i]}/tunnels/count")"
		fi
		tunnels="$(generate_tag 'td' "$tunnels")"

		if [ ! -d "${userdirs[$i]}/levels" ]; then
			levels='0'
		else
			levels="$(<"${userdirs[$i]}/levels/count")"
		fi
		levels="$(generate_tag 'td' "$levels")"
		
		date="$(timestamp_to_date "$(<"${userdirs[$i]}/timestamp")")"
		date="$(generate_tag 'td' "$date")"

		user="$username $tunnels $levels $date"
		user="$(generate_tag 'tr' "$user")"
		printf '%s' "$user"
	done
}

content() {
	users="$(users)"
	printf '%s' "$(<"$static_path/userdir.html")" | \
		replace_all '<!-- USERS -->' "$users"
}

title() {
	printf 'user directory'
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
