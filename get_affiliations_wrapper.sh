#! /bin/bash

while read line; do
	get_affiliations.py $line
done < $1
