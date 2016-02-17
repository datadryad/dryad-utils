#!/bin/sh

#
# Takes one argument, which is the item ID of a data file object.
# Returns a list of the 20 IP addresses that have downloaded this 
# file the most, along with the number of downloads for each IP.

if [ "$#" -ne 1 ]; then
    echo "Usage: statsMostDownloadsOfFile.sh file_item_id"
    exit
fi

curl -# "http://datadryad.org/solr/statistics/select/?indent=on&fl=ip&rows=10000000&q=-isBot:true+owningItem:$1" | grep ip | sort | uniq -c | sort -rn | head -20

