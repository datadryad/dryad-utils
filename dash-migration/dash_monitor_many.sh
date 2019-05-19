#!/bin/bash

# Processes a list of items (handles) that have been migrated to DASH,
# checking whether they have been stored in Merritt.

# It is assumed that the list of items is stored in a
# file in the current directory called items.txt,
# with one Handle per line.

echo Monitoring items that have been transferred DASH...

set -e

while read item; do
    echo Monitoring $item
    /opt/dryad/bin/dspace curate -v -t dashmonitor -i $item -r - >>dashMonitor.log
done <items.txt

echo

