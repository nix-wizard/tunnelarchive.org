#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

. ../../../lib.sh


enforce 'GET' "$REQUEST_METHOD"

declare -A queries
cd "$static_path/assets/image"

skybox="$((0 + $RANDOM % 11))"

header 'Content-Type: image/png'
header ''

cat "./$skybox.png"
