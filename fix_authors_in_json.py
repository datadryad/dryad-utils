#!/usr/bin/env python

# fix errors in database

__author__ = 'daisieh'

import re
import os
import sys
import json

def rows_from_query(sql):
    # Now execute it
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    output = [line.strip().split('|') for line in os.popen(cmd).readlines()]
    if len(output) <= 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        return output[1:-1]

def update_json(manuscript_id, json_data):
	manuscript = json.loads(json_data)
	print manuscript


def main():
    bad_json_rows = rows_from_query("select manuscript_id, json_data from manuscript where json_data like '%htmlfamilyName%'")
    for entry in bad_json_rows:
        update_json(entry[0], entry[1])

if __name__ == '__main__':
    main()

