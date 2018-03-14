#!/usr/bin/env python

## This script removes files associated with a bitstream ID from the temporary web store.

__author__ = 'daisie'

import re
import os
import sys
import subprocess

WEB_ASSETS_BUCKET = "dryad-web-assets/temporary"

def get_bitstream_id():
    matched_bitstream_id = None
    matchers = (
       'http.*bitstream\/id\/(\d+)\/.*',
       'http.*bitstreamID=(\d+).*',
       '(\d+)',
    )
    while matched_bitstream_id is None:
        raw = raw_input('Enter the bitstream ID or URL: ')
        for matcher in matchers:
            matched_bitstream_id = re.match(matcher, raw)
            if matched_bitstream_id is not None:
                break
    return int(matched_bitstream_id.group(1))

def main():
    bitstream_id = None
    if len(sys.argv) == 3:
        bitstream_id = int(sys.argv[1])
    else:
        bitstream_id = get_bitstream_id()

    print "Checking existence of file"
    cmd = 'aws s3 rm "s3://%s" --recursive --exclude "*" --include "%s.*"' % (WEB_ASSETS_BUCKET, bitstream_id)
    subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    
if __name__ == '__main__':
    main()

