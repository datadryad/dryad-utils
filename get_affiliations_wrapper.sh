#! /bin/bash

# get_affiliations_wrapper.sh [affiliation/funder/publisher] <doi-list-file>

REPORT=$1

while read line; do
	get_affiliations.py --doi $line --report $REPORT
done < $2
