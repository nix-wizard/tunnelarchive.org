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

game="$(<"./game")"
name="$(<"./name")"
author="$(<"./author/username")"

header 'Content-Type: application/octet-stream'
header "Content-Disposition: attachment; filename=\"$tunnelid.run.$game.tunnel\""
header ''

printf '!name=%s+\n!author=%s+\n!id=%s+\n' "$name" "$author" "$tunnelid"
for level in ./levels/*/; do
	printf '%s+\n' "$(<"$level/data")"
done
