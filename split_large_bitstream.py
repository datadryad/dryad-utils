#!/usr/bin/env python

## This script downloads a bitstream from the assetstore, splits it into pieces, and 
## uploads the pieces to accessible URLs. 
## Make sure you've set the ASSETSTORE_BUCKET environment variable in your account.
## Optional arguments are a bitstream ID and the number of chunks to split into.

__author__ = 'daisie'

import re
import os
import sys
import json
import tempfile
import subprocess
from sql_utils import dict_from_query, sql_query

WEB_ASSETS_BUCKET = "dryad-web-assets/temporary"
ASSETSTORE_BUCKET = os.environ['ASSETSTORE_BUCKET']
TEMP_DIR = '/transfer-complete/temp'

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

class bitstream_file(object):
    def __init__(self, s3key, bucket):
        self.s3key = s3key
        cmd = 'aws s3api head-object --bucket %s --key "%s"' % (bucket, s3key)
        metadata = json.load(os.popen(cmd))
        self.size = metadata['ContentLength']
        self.name = os.path.basename(self.s3key)
        self.mimetype = metadata['ContentType']
        if 'md5' in metadata['Metadata']:
            self.md5 = metadata['Metadata']['md5']
        else:
            self.md5 = metadata['ETag']
            if '-' in self.md5:
                print "Can't find MD5"
                exit(1)
    def __unicode__(self):
        return u'Name: %s, Size: %d, MD5: %s, Mime-Type: %s' % (self.name, self.size, self.md5, self.mimetype)

def get_object_key(bitstream_id):
    bitstream_dict = query_bitstream_table(bitstream_id)
    if bitstream_dict is None:
        raise Exception("Unable to get bitstream info from database")
    internal_id = bitstream_dict['internal_id']
    return internal_id

def query_bitstream_table(bitstream_id):
    '''
    Returns a dict of values for the bitstream id
    '''
    sql = 'SELECT bitstream_format_id, name, size_bytes, checksum, checksum_algorithm, source, internal_id ' \
          'FROM bitstream WHERE bitstream_id = %d' % bitstream_id
    return dict_from_query(sql)

def main():
    bitstream_id = None
    num_chunks = 2
    if len(sys.argv) == 3:
        bitstream_id = int(sys.argv[1])
        num_chunks = sys.argv[2]
    else:
        bitstream_id = get_bitstream_id()
        num_chunks = raw_input('Enter the number of chunks: ')

    print "Checking existence of file"
    largefile = bitstream_file(get_object_key(bitstream_id), ASSETSTORE_BUCKET)
    localfile = TEMP_DIR + '/' + largefile.name
    tempdir = tempfile.mkdtemp(dir=TEMP_DIR)
    print "Copying file to " + localfile
    cmd = 'aws s3 cp "s3://%s/%s" %s' % (ASSETSTORE_BUCKET, largefile.s3key, localfile)
    subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    
    print "Splitting file into %s pieces" % (num_chunks)
    cmd = 'split -n %s -d %s %s/%s.' % (num_chunks, localfile, tempdir, bitstream_id)
    os.popen(cmd)
    
    output_urls = []
    for file in os.listdir(tempdir):
        # upload each one
        s3path = WEB_ASSETS_BUCKET + '/' + file
        cmd = 'aws s3 cp %s/%s "s3://%s"' % (tempdir, file, s3path)
        subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        output_urls.append('https://s3.amazonaws.com/' + s3path)
    
    os.popen('rm -R %s' % (tempdir))
    os.popen('rm %s' % (localfile))
    
    print "Split files are at:"
    for url in output_urls:
        print url

if __name__ == '__main__':
    main()

