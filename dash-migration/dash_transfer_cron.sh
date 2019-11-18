#!/bin/bash

# Processes a list of items (handles) to be migrated to DASH

# It is assumed that the list of items is stored in a
# file in the current directory called items.txt,
# with one Handle per line.

echo Processing items into DASH...

set -e

TRANSFILE="/home/ubuntu/dryad-utils/dash-migration/items-$1.txt"

echo Reading file $TRANSFILE

while read item; do
    echo Transferring $item
    /opt/dryad/bin/dspace curate -v -t transfertodash -i $item -r - >>dashTransfer.log
done <$TRANSFILE

echo

