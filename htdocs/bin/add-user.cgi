#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../lib.sh


enforce 'POST' "$REQUEST_METHOD"
enforce 'same-origin' "$HTTP_SEC_FETCH_SITE"

mkdir -p "$db_path/users"
mkdir -p "$db_path/users/by-username"
mkdir -p "$db_path/users/by-ip"
mkdir -p "$db_path/users/by-timestamp"
cd "$db_path/users"

declare -A body
parse_values "$(</dev/stdin)" body
assert_var "${body[username]-}"
assert_var "${body[password]-}"
assert_var "${body[confirm]-}"
username="${body[username]-}"
password="${body[password]-}"
confirm="${body[confirm]-}"
check_username "$username"
check_unprintable "$password"
enforce_length "$password" '128'
check_unprintable "$confirm"
enforce_length "$confirm" '128'

if [[ -z "${HTTP_X_REAL_IP-}" ]]; then # ONLY FOR TEST ENVIRONMENT WHEN NOT BEHIND REVERSE PROXY
	HTTP_X_REAL_IP="${REMOTE_ADDR-}"
fi
ip="${HTTP_X_REAL_IP}" # ONLY CORRECT WHEN BEHIND THE REVERSE PROXY
ip="$(sha256sum <<<"$ip" | cut -f 1 -d " ")"
timestamp="$(date -u +%s%N)"

if ! mkdir "./by-username/$username"; then
	return_status 403 "This username is already taken."
fi

if [ "$password" != "$confirm" ]; then
	return_status 403 "Passwords do not match."
fi

if [ -h "./by-ip/$ip" ] || [ -e "./by-ip/$ip" ]; then # if this ip has already posted
	return_status '403' 'Sorry, only one account is allowed per IP.'
fi

password="$(openssl passwd -apr1 "$password")"
printf '%s:%s\n' "$username" "$password" >> "$db_path/users/.htpasswd"

ln -s "../by-username/$username" "./by-ip/$ip"
ln -s "../by-username/$username" "./by-timestamp/$timestamp"

cd "./by-username/$username"

printf '%s' "$username" > username
printf '%s' "$ip" > ip
printf '%s' "$timestamp" > timestamp

header 'Content-Type: text/html'
header ''

printf '%s\n' "$stylesheet"
printf '<p style="color: #00FF00">Success! <a href="/user/edit-profile.cgi" target="_top">Edit your profile</a></p>\n'
