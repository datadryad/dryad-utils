#!/usr/bin/env python

# Move bitstreams from local assetstore to S3 bucket

__author__ = 'daisie'

import os
import re
import sys
import json
import hashlib
from sql_utils import list_from_query, sql_query

ASSETSTORE_BUCKET = os.environ['ASSETSTORE_BUCKET']
ASSETSTORE_PATH = '/opt/dryad-data/assetstore/'

def get_assetstore_path(internal_id):
    parts = (internal_id[0:2],internal_id[2:4],internal_id[4:6])
    return ASSETSTORE_PATH + '/'.join(parts) + '/' + internal_id

def validate_s3_file(bitstream):
    cmd = 'aws s3api head-object --bucket %s --key "%s"' % (ASSETSTORE_BUCKET, bitstream['internal_id'])
    result = os.popen(cmd).read()
    if (result != ""):
        metadata = json.loads(result)
        if ('md5' in metadata['Metadata']):
            if (long(bitstream['size_bytes']) == long(metadata['ContentLength'])) and (bitstream['checksum'] == metadata['Metadata']['md5']):
                return True
    return False
    
def update_database(bitstream_id):
    print "Updating database..."
    print sql_query("update bitstream set store_number=1 where bitstream_id=%s" % (bitstream_id)).read()

def main():
    if len(sys.argv) == 2:
        bitstream_id = int(sys.argv[1])
        bitstreams = list_from_query("select bitstream_id, internal_id, checksum, size_bytes from bitstream where bitstream_id=%s" % (bitstream_id))
    else:
        print "Gathering bitstreams..."
        bitstreams = list_from_query("select bitstream_id, internal_id, checksum, size_bytes from bitstream where deleted=false and store_number=0 order by bitstream_id ASC")

    print "Processing %d local bitstreams" % (len(bitstreams))

    for bitstream in bitstreams:
        internal_id = bitstream['internal_id']
        md5 = bitstream['checksum']
        bitstream_id = bitstream['bitstream_id']        
        size = bitstream['size_bytes']
        
        print "Checking to see if %s exists at S3..." % (internal_id)
        if (validate_s3_file(bitstream)):
            print "File %s already exists at S3" % (internal_id)
            update_database(bitstream_id)
        else:
            print "Copying %s to s3..." % (internal_id)
            sys.stdout.flush()
            cmd = 'aws s3 cp "%s" "s3://%s/%s" --metadata md5=%s --expected-size=%s' % (get_assetstore_path(internal_id), ASSETSTORE_BUCKET, internal_id, md5, size)
            if (os.popen(cmd).close() is None):
                print "Verifying file size and md5 of %s..." % (internal_id)
                if validate_s3_file(bitstream):
                    update_database(bitstream_id)
                else:
                    print "S3 copy does not match local copy, skipping database update."
            else:
                print "AWS copy error, exiting"
                exit(1)
        
        sys.stdout.flush()
    
    print "Done."
        
if __name__ == '__main__':
    main()

