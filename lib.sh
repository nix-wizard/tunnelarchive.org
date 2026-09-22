#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

server_name='tunnelarchive.org'

root_url="https://$server_name/"

data_path="/var/www/$server_name/"
htdocs_path="$data_path/htdocs/"
static_path="$data_path/static/"
db_path="/var/lib/$server_name/"
base_path="$static_path/base.html"

stylesheet='<link rel="stylesheet" href="/assets/style/minimal.css">'

replace_all() {
	local placeholder=$1
	local replacement=$2
	local content

	replacement=${replacement//&/\\&}
	content=$(</dev/stdin)
	printf '%s\n' "${content//$placeholder/$replacement}"
}

generate_tag()
{
	local tag="$1"
	local content="$2"

	printf '<%s>%s</%s>\n' "$tag" "$content" "$tag"
}

generate_link()
{
	local content="$1"
	local href="$2"

	printf '<a href="%s">%s</a>\n' "$href" "$content"
}

generate_dirlist()
{
	local directory="$1"

	for dir in "$directory"/*/; do
		local dirname=$(basename "$dir")
		generate_tag h2 "$(generate_link "./$dirname/" "./$dirname/")"
		printf '<br>\n'
	done
	for file in "$directory"/*; do
		local filename=$(basename "$file")
		if [ -f "$file" ] && [ "$filename" != "index.html" ]; then
			generate_tag h2 "$(generate_link "./$filename" "./$filename")"
			printf '<br>'
		fi
	done
}

generate_page()
{
	local content="$1"
	local title="$2"
	local page="$3"
	
	replace_all '<!-- CONTENT -->' "$content" < "$base_path" | \
	replace_all '<!-- TITLE -->' "$title" | \
	replace_all '<!-- PAGE -->' "$page"
}

header() {
	local clrf=$'\r\n'
	printf '%s%s' "$1" "$clrf"
}

url_decode() {
	local data="${1//+/ }"
	printf '%b' "${data//%/\\x}"
}

parse_values() {
	local encoded="$1"
	local -n result="$2"

	local IFS='&'
	local pairs
	read -ra pairs <<<"$encoded"

	local pair key value
	for pair in "${pairs[@]}"; do
		IFS='=' read -r key value <<<"$pair"
		result["$(url_decode "$key")"]="$(url_decode "$value")"
	done
}


return_status() {
	local code="$1"
	local message="$2"

	header 'Content-Type: text/html'
	header "Status: $code"
	header ''
	printf '%s\n' "$stylesheet"
	printf '<p style="color: #FF0000;"">%s</p>\n' "$message"
	exit
}

assert_var() {
	if [ -z "$1" ]; then
		return_status "400" "bad request"
	fi
}

html_escape() {
	local s
	s=$(</dev/stdin)

	s=${s//&/\&amp;}
	s=${s//</\&lt;}
	s=${s//>/\&gt;}
	s=${s//\"/\&quot;}
	s=${s//\'/\&\#39;}

	printf '%s' "$s"
}

timestamp_to_date() {
	local timestamp=$1
	if [[ "$(date -r 0 +%s 2>/dev/null)" == "0" ]]; then
		# BSD date
		date -u -r "$((timestamp / 1000000000))" +%F
	else
		# GNU date
		date -u -d "@$((timestamp / 1000000000))" +%F
	fi
}
strip_newlines() {
	local input="$1"

	input="${input%$'\r'}"
	input="${input%$'\n'}"

	printf '%s' "$input"
}

enforce() {
	local required="$1"
	local request="$2"

	if [[ "$request" != "$required" ]]; then
		return_status "400" "bad request"
	fi
}

enforce_length() {
	local string="$1"
	local length="$2"

	# input length validation
	if ((${#string} > "$length")); then
		return_status '400' "Must be at most $length characters."
	fi
}

check_unprintable() {
	local string="$1"
	if printf '%s' "$string" | grep -q '[[:cntrl:]]'; then
		return_status '400' "Bad request: bad characters"
	fi
}

check_username() {
	local username="$1"

	check_unprintable "$username"
	enforce_length "$username" '32'
	# enforce characters
	if [[ ! "$username" =~ ^[a-z0-9_]+$ ]]; then
		return_status '400' 'Only a-z, 0-9, and _ allowed.'
	fi
}

enforce_number() {
	local number="$1"
	
	if [[ ! "$number" =~ ^[0-9]+$ ]]; then
		return_status '400' 'Not a number.'
	fi
}

game_to_string() {
	game="$1"

	if [ "$game" == "1" ]; then
		printf 'Run'
	elif [ "$game" == "2" ]; then
		printf 'Run 2'
	elif [ "$game" == "3" ]; then
		printf 'Run 3'
	elif [ "$game" == "3.1" ]; then
		printf 'Run 3 import/export mod'
	else
		return_status '500' 'Bad game value'
	fi
}

