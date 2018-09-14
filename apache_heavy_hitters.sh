#!/usr/bin/env bash

echo "Heaviest users of Apache today..."
awk '{print $1}' /home/ubuntu/apache/log/datadryad.org-access.log | sort | uniq -c | sort -nr | head -10

