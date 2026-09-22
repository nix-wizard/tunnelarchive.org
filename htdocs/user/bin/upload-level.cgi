#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../../lib.sh


enforce 'POST' "$REQUEST_METHOD"
enforce 'same-origin' "$HTTP_SEC_FETCH_SITE"

username="$REMOTE_USER"
user_dir="$db_path/users/by-username/$username"

mkdir -p "$db_path/levels/by-levelid"
mkdir -p "$db_path/levels/by-timestamp"
mkdir -p "$user_dir/levels/by-levelid"
mkdir -p "$user_dir/levels/by-timestamp"
cd "$db_path/levels"

declare -A body
parse_values "$(</dev/stdin)" body
assert_var "${body[name]-}"
assert_var "${body[data]-}"
assert_var "${body[game]-}"
assert_var "${body[difficulty]-}"
name="${body[name]-}"
description="${body[description]-}"
data="${body[data]-}"
attribution="${body[attribution]-}"
difficulty="${body[difficulty]-}"
game="${body[game]-}"
license="${body[license]-}"
check_unprintable "$name"
check_unprintable "$difficulty"
check_unprintable "$game"
check_unprintable "$attribution"
check_unprintable "$license"
enforce_length "$name" '64'
enforce_length "$description" '512'
enforce_length "$data" '65536'
enforce_length "$difficulty" '2'
enforce_length "$game" '3'
enforce_length "$attribution" '8'
enforce_length "$license" '8'
enforce_number "$difficulty"
if [ ! $game == "1" ] && [ ! $game == "2" ] && [ ! $game == "3" ] && [ ! $game == "3.1" ]; then
	return_status '400' 'Invalid game.'
fi
if [ ! -z "$attribution" ]; then
	enforce_number "$attribution"
fi
if [ ! -d "./by-levelid/$attribution" ]; then
	return_status '400' 'Nonexistent level ID.'
fi
if [ ! "$license" == "accepted" ]; then
	return_status '403' 'You must accept the terms.'
fi
if (( difficulty > 10 || difficulty < 0 )); then
	return_status '400' 'Invalid difficulty.'
fi

timestamp="$(date -u +%s%N)"

if [ -f ./current-levelid ]; then
	levelid="$(<'./current-levelid')"
	((levelid=levelid+1))
else
	levelid='0'
fi
printf '%s' "$levelid" > ./current-levelid

mkdir "./by-levelid/$levelid"
ln -s "../by-levelid/$levelid" "./by-timestamp/$timestamp"
ln -s "../../../../../levels/by-levelid/$levelid" "$user_dir/levels/by-levelid/$levelid"
ln -s "../../../../../levels/by-levelid/$levelid" "$user_dir/levels/by-timestamp/$timestamp"
ln -s "../../../users/by-username/$username" "$db_path/levels/by-levelid/$levelid/author"
if [ -f "$user_dir/levels/count" ]; then
	count="$(<"$user_dir/levels/count")"
	((count=count+1))
else
	count='1'
fi
printf '%s' "$count" > "$user_dir/levels/count"

cd "./by-levelid/$levelid"

printf '%s' "$name" > name
printf '%s' "$description" > description
printf '%s' "$levelid" > levelid
printf '%s' "$data" > data
printf '%s' "$difficulty" > difficulty
printf '%s' "$game" > game
printf '%s' "$attribution" > attribution
printf '%s' "$timestamp" > timestamp

header 'Content-Type: text/html'
header ''

printf '%s\n' "$stylesheet"
printf '<p style="color: #00FF00">Success! <a href="/level.cgi?levelid=%s" target="_top">See your level</a></p>\n' "$levelid"
