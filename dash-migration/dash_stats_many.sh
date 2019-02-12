#!/bin/bash

# Processes a list of items (handles) for statistics to be migrated to DASH

# It is assumed that the list of items is stored in a
# file in the current directory called items.txt,
# with one Handle per line.

echo Processing statistics into DASH format...

set -e

while read item; do
    /opt/dryad/bin/dspace curate -v -t dashstats -i $item -r - >>dashStats.log
done <items.txt

echo



