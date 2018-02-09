#!/usr/bin/env python

# Verify that all bitstreams in the database are reflected correctly in the assetstore.

__author__ = 'daisie'

import os
import re
import sys
import json
import hashlib
from sql_utils import list_from_query, sql_query

ASSETSTORE_BUCKET = os.environ['ASSETSTORE_BUCKET']

def validate_s3_file(bitstream):
    cmd = 'aws s3api head-object --bucket %s --key "%s"' % (ASSETSTORE_BUCKET, bitstream['internal_id'])
    result = os.popen(cmd).read()
    if (result != ""):
        metadata = json.loads(result)
        if ('md5' in metadata['Metadata']):
            if (long(bitstream['size_bytes']) == long(metadata['ContentLength'])) and (bitstream['checksum'] == metadata['Metadata']['md5']):
                return True
    return False
    
def main():
    print "Gathering bitstreams..."
    bitstreams = list_from_query("select bitstream_id, internal_id, checksum, size_bytes from bitstream where deleted=false order by bitstream_id desc")
    print "Processing %d local bitstreams" % (len(bitstreams))
    count = len(bitstreams)
    for bitstream in bitstreams:
        internal_id = bitstream['internal_id']
        md5 = bitstream['checksum']
        bitstream_id = bitstream['bitstream_id']        
        size = bitstream['size_bytes']
        
        if (validate_s3_file(bitstream)):
            print "%s: File %s is valid" % (count, internal_id)
        else:
            print "%s: ERROR: File %s doesn't match" % (count, internal_id)
        count = count - 1
        sys.stdout.flush()
    
    print "Done."
        
if __name__ == '__main__':
    main()

