#!/usr/bin/env python

__author__ = 'daisie'

import os
import re

def main():
    cmd = 'aws s3 ls s3://dryad-ftp/ --recursive'
    results = list(os.popen(cmd))
    for file in results:
        parts = re.split('\s+', file, 3)
        if (re.match("^\.", parts[3]) is None):
            print parts[3].rstrip()

if __name__ == '__main__':
    main()

