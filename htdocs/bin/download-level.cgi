#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../lib.sh


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

game="$(<"./game")"

header 'Content-Type: application/octet-stream'
header "Content-Disposition: attachment; filename=\"$levelid.run.$game.level\""
header ''

printf '%s\n' "$(<"./data")"
