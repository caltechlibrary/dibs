#!/bin/bash

function check_manifest() {
	if ! jq . "$1" > /dev/null; then
		echo "ERROR: ${1} failed to parse.";
		jq . "${1}"
	else
		echo "${1}, OK"
	fi
}

ls -1 manifests/*.json | while read FNAME; do
	check_manifest "${FNAME}"
done
