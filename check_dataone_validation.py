#!/usr/bin/env python
__author__ = 'dan'

import sys
import csv

# type	object	code	output	content
def row_is_ok(dict_row):
    if dict_row['code'] == '0':
        return True
    elif dict_row['code'] == '-1':
        return True
    elif dict_row['code'] == '1' and 'validates' in dict_row['output']:
        return True
    else:
        return False

def validate(filename):
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(sys.stdout, reader.fieldnames)
        writer.writeheader()
        for dict_row in reader:
            if not row_is_ok(dict_row):
                writer.writerow(dict_row)
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <infile>" % sys.argv[0]
    else:
        validate(sys.argv[1])