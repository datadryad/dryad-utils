#!/usr/bin/env python

## This replaces large files synced to the dryad-ftp bucket at S3 
## to the designated S3 assetstore. 
## Make sure you've set the ASSETSTORE_BUCKET environment variable in your account.

__author__ = 'dan'

import re
import os
import sys
import json
from sql_utils import dict_from_query

FTP_BUCKET = "dryad-ftp"
ASSETSTORE_BUCKET = os.environ['ASSETSTORE_BUCKET']

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

def get_largefile_key():
    return raw_input('Enter the s3 key to the large file: ')

def get_object_key(bitstream_id):
    bitstream_dict = query_bitstream_table(bitstream_id)
    if bitstream_dict is None:
        raise Exception("Unable to get bitstream info from database")
    internal_id = bitstream_dict['internal_id']
    return internal_id

def rename_object(bitstream_id, largefile):
    destination_key = get_object_key(bitstream_id)
    print "Copying '%s' -> '%s'" % (largefile.s3key, destination_key)
    cmd = 'aws s3 cp "s3://%s/%s" "s3://%s/%s" --metadata md5=%s' % (FTP_BUCKET, largefile.s3key, ASSETSTORE_BUCKET, destination_key, largefile.md5)
    os.popen(cmd)

def query_bitstream_table(bitstream_id):
    '''
    Returns a dict of values for the bitstream id
    '''
    sql = 'SELECT bitstream_format_id, name, size_bytes, checksum, checksum_algorithm, source, internal_id ' \
          'FROM bitstream WHERE bitstream_id = %d' % bitstream_id
    return dict_from_query(sql)

def query_bitstream_format(large_file):
#     sql = "SELECT bitstream_format_id FROM bitstreamformatregistry where mimetype = '%s'" % mimetype
    extension = ""
    extension_match = re.match("^.*\.(.+)$", large_file.name)
    if extension_match != None:
        extension = extension_match.group(1)  
    sql = "SELECT bitstreamformatregistry.* FROM bitstreamformatregistry, fileextension WHERE fileextension.extension LIKE '%s' AND bitstreamformatregistry.bitstream_format_id=fileextension.bitstream_format_id" % extension
    return dict_from_query(sql)

def verify_file(bitstream_id):
    '''
    Looks up the file info in the database, verifies its size and md5 sum against what's in postgres
    '''
    file_dict = query_bitstream_table(bitstream_id)
    if file_dict is None:
        print "No file found for bitstream_id %d" % bitstream_id
        return False
    file = bitstream_file(file_dict['internal_id'], ASSETSTORE_BUCKET)
    # size
    if int(file_dict['size_bytes']) != file.size:
        print "Size mismatch: %d / %d" % (int(file_dict['size_bytes']), file.size)
        return False
    # md5
    if file_dict['checksum'] != file.md5:
        print "MD5 mismatch: %s / %s" % ( file_dict['checksum'], file.md5)
        return False
    return True

def update_bitstream_table(bitstream_id, large_file):
    format_dict = query_bitstream_format(large_file)
    if format_dict is None or format_dict['bitstream_format_id'] == "(0 rows)":
        format_id = 1
    else:
        format_id = format_dict['bitstream_format_id'] # stays a string
    sql = "UPDATE bitstream set size_bytes=%d, name='%s', source='%s' ,checksum='%s', bitstream_format_id=%s where bitstream_id = %d" % (
        large_file.size,
        large_file.name,
        large_file.name,
        large_file.md5,
        format_id,
        bitstream_id
    )
    print "Executing SQL: %s" % sql
    cmd = "psql -U dryad_app dryad_repo -c \"%s\"" % sql
    print os.popen(cmd).read()


def main():
    bitstream_id = None
    largefile_key = ""
    if len(sys.argv) == 3:
        bitstream_id = int(sys.argv[1])
        largefile_key = sys.argv[2]
    else:
        bitstream_id = get_bitstream_id()
        largefile_key = get_largefile_key()
    print "Bitstream ID: %d" % bitstream_id

    largefile = None
    try:
        print "Checking existence of dummy file %s..." % (get_object_key(bitstream_id))
        dummyfile = bitstream_file(get_object_key(bitstream_id), ASSETSTORE_BUCKET)
        largefile = bitstream_file(largefile_key, FTP_BUCKET)
    except BaseException as e:
        print "Unable to read file: %s" % e
        exit(-1)

    # Update the bitstream table
    rename_object(bitstream_id, largefile)
    update_bitstream_table(bitstream_id, largefile)

    # Verify the replaced file is right
    result = verify_file(bitstream_id)

    if result == True:
        print "SUCCESS: local copy in transfer-complete can be deleted."
        sys.exit(0)
    else:
        print "FAILURE: please report the output of this script to devs."
        sys.exit(1)

if __name__ == '__main__':
    main()

