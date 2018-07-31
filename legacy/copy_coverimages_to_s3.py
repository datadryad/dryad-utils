#!/usr/bin/env python

# Script to move coverimages from dryad-repo to the s3 bucket.
# Pass in a file that contains a list of image file names (not paths) to copy over.

__author__ = 'daisie'

import os
import re
import sys
import json
import hashlib

def main():
    if len(sys.argv) < 3:
        print "Source and target buckets are required as arguments"
        exit(0)
    sourcefile = sys.argv[1]
    targetbucket = sys.argv[2]

    with open(sourcefile) as infile:
        files = infile.readlines()
        for file in files:
            file = file.rstrip()
            key = os.path.basename(file)
            cmd = 'aws s3 cp "/opt/dryad/webapps/xmlui%s" "s3://%s/coverimages/%s"' % (file, targetbucket, key)
            print cmd
            os.popen(cmd)
            sys.stdout.flush()            

if __name__ == '__main__':
    main()

