#! /bin/bash

cd /dryad-data/transfer-complete/
#/bin/date > /tmp/complete.txt
find /dryad-data/transfer-complete/ ! -name '.*' -mtime -1 > /tmp/complete.txt
cat /tmp/complete.txt | mail -s "Transferred files are complete" curator-internal@datadryad.org
