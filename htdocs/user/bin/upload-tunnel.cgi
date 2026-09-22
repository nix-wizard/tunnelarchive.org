#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../../lib.sh


enforce 'POST' "$REQUEST_METHOD"
enforce 'same-origin' "$HTTP_SEC_FETCH_SITE"

username="$REMOTE_USER"
user_dir="$db_path/users/by-username/$username"

mkdir -p "$db_path/tunnels/by-tunnelid"
mkdir -p "$db_path/tunnels/by-timestamp"
mkdir -p "$user_dir/tunnels/by-tunnelid"
mkdir -p "$user_dir/tunnels/by-timestamp"
cd "$db_path/tunnels"

declare -A body
parse_values "$(</dev/stdin)" body
assert_var "${body[name]-}"
assert_var "${body[data]-}"
assert_var "${body[game]-}"
assert_var "${body[difficulty]-}"
name="${body[name]-}"
description="${body[description]-}"
data="${body[data]-}"
difficulty="${body[difficulty]-}"
game="${body[game]-}"
license="${body[license]-}"
check_unprintable "$name"
check_unprintable "$difficulty"
check_unprintable "$game"
enforce_length "$name" '64'
enforce_length "$description" '512'
enforce_length "$data" '1024'
enforce_length "$difficulty" '2'
enforce_length "$game" '3'
enforce_number "$difficulty"
if [ ! $game == "1" ] && [ ! $game == "2" ] && [ ! $game == "3" ] && [ ! $game == "3.1" ]; then
	return_status '400' 'Invalid game.'
fi
if (( difficulty > 10 || difficulty < 0 )); then
	return_status '400' 'Invalid difficulty.'
fi

i=0
while read -r levelid; do
	((i=i+1))
	if [ "$levelid" ]; then
		levelid="$(strip_newlines "$levelid")"
		enforce_length "$levelid" 8
		enforce_number "$levelid"
		if [ ! -d "$db_path/levels/by-levelid/$levelid" ]; then
			return_status '400' "$levelid is not a valid level ID."
		fi

		levelgame="$(<"$db_path/levels/by-levelid/$levelid/game")"
		if [ "$game" != "$levelgame" ]; then # Run 3 levels are compatible with the Import/Export mod
			if [ "$game" == "3.1" ] && [ "$levelgame" == "3" ]; then
				continue
			fi
			return_status '400' "$levelid is not compatible with this tunnel's game."
		fi
	fi
done <<<"$data"
count="$i"

timestamp="$(date -u +%s%N)"

if [ -f ./current-tunnnelid ]; then
	tunnelid="$(<'./current-tunnelid')"
	((tunnelid=tunnelid+1))
else
	tunnelid='0'
fi
printf '%s' "$tunnelid" > ./current-tunnelid

mkdir "./by-tunnelid/$tunnelid"
ln -s "../by-tunnelid/$tunnelid" "./by-timestamp/$timestamp"
ln -s "../../../../../tunnels/by-tunnelid/$tunnelid" "$user_dir/tunnels/by-tunnelid/$tunnelid"
ln -s "../../../../../tunnels/by-tunnelid/$tunnelid" "$user_dir/tunnels/by-timestamp/$timestamp"
ln -s "../../../users/by-username/$username" "./by-tunnelid/$tunnelid/author"
if [ -f "$user_dir/tunnels/count" ]; then
	count="$(<"$user_dir/tunnels/count")"
	((count=count+1))
else
	count='1'
fi
printf '%s' "$count" > "$user_dir/tunnels/count"

cd "./by-tunnelid/$tunnelid"

printf '%s' "$name" > name
printf '%s' "$description" > description
printf '%s' "$tunnelid" > tunnelid
printf '%s' "$data" > data
printf '%s' "$difficulty" > difficulty
printf '%s' "$game" > game
printf '%s' "$count" > count
printf '%s' "$timestamp" > timestamp

mkdir levels
i=0
while read -r levelid; do
	((i=i+1))
	levelid="$(strip_newlines "$levelid")"
	if [ "$levelid" ]; then
		ln -s "../../../../levels/by-levelid/$levelid" "./levels/$levelid"
		mkdir -p "$db_path/levels/by-levelid/$levelid/tunnels"
		ln -s "../../../../tunnels/by-tunnelid/$tunnelid" "$db_path/levels/by-levelid/$levelid/tunnels/$tunnelid"
	fi
done <<<"$data"

mkdir levelauthors
i=0
for level in ./levels/*/; do
	levelauthor="$(<"$level/author/username")"
	if [ ! -L "./levelauthors/$((i+1))" ]; then
		((i=i+1))
		ln -s "../../../../users/by-username/$levelauthor" "./levelauthors/$i"
	fi
done

header 'Content-Type: text/html'
header ''

printf '%s\n' "$stylesheet"
printf '<p style="color: #00FF00">Success! <a href="/tunnel.cgi?tunnelid=%s" target="_top">See your tunnel</a></p>\n' "$tunnelid"
