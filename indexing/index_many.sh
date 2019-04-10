#!/bin/bash

# Processes a list of item IDs  to be reindexed in DSpace-Dryad

# It is assumed that the list of items is stored in a
# file in the current directory called items.txt,
# with one item ID per line.

echo Processing items to reindex

set -e

while read item; do
    echo "#### Indexing $item ############################################"
    /opt/dryad/bin/dspace update-discovery-index -i $item >>indexing.log
done <items.txt

echo



