#!/usr/bin/env python

__author__ = 'dan'

import re
import os
import hashlib
import mimetypes

ASSETSTORE_PATH = '/opt/dryad-data/assetstore/'

def check_write_access():
    return os.access(ASSETSTORE_PATH,os.W_OK)

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
    def __init__(self,path):
        self.path = path
        self.size = os.path.getsize(self.path)
        self.name = os.path.basename(self.path)
        self.mimetype = mimetypes.guess_type(self.path)[0]
    def md5(self):
        '''
        hashlib md5 file implementation from http://joelverhagen.com/blog/2011/02/md5-hash-of-file-in-python/
        '''
        with open(self.path, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(65536)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()
    def check_mimetype(self):
        # If the mime type is none, prompt for it
        print "Unable to guess MIME type"
        while self.mimetype is None:
            raw = raw_input("Please enter a MIME type or leave blank for 'application/octet-stream': ")
            if len(raw) == 0:
                self.mimetype = 'application/octet-stream'
            else:
                self.mimetype = raw
            if query_bitstream_format(self.mimetype) is None:
                print "MIME type %s not found in bitstreamformat table, please try again." % self.mimetype
                self.mimetype = None
        print "Using MIME type %s" % self.mimetype

    def __unicode__(self):
        return u'Name: %s, Size: %d, MD5: %s, Mime-Type: %s' % (self.name, self.size, self.md5(), self.mimetype)

def get_largefile_path():
    return raw_input('Enter the path on the filesystem to the large file: ')

def verify_file(bitstream_id, file):
    '''
    Looks up the file info in the database, verifies its size and md5 sum against what's in postgres
    '''
    file_dict = query_bitstream_table(bitstream_id)
    # size
    if int(file_dict['size_bytes']) != file.size:
        print "Size mismatch: %d / %d" % (int(file_dict['size_bytes']), file.size)
        return False
    # md5
    calculated_md5 = file.md5()
    if file_dict['checksum'] != calculated_md5:
        print "MD5 mismatch: %s / %s" % ( file_dict['checksum'], calculated_md5)
        return False
    return True

def get_assetstore_path(bitstream_id):
    bitstream_dict = query_bitstream_table(bitstream_id)
    if bitstream_dict is None:
        raise Exception("Unable to get bitstream info from database")
    internal_id = bitstream_dict['internal_id']
    parts = (internal_id[0:2],internal_id[2:4],internal_id[4:6])
    return ASSETSTORE_PATH + '/'.join(parts) + '/' + internal_id

def place_largefile(bitstream_id, largefile):
    destination_path = get_assetstore_path(bitstream_id)
    if not os.access(destination_path, os.W_OK):
        raise Exception("Unable to get write access on the destination path")
    # os.rename(largefile.path, destination_path)
    # TODO: Actually rename the file
    print "Rename %s -> %s" % (largefile.path, destination_path)

def dict_from_query(sql):
    # Now execute it
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    output = [line.strip().split('|') for line in os.popen(cmd).readlines()]
    if len(output) == 1:
        return None
    else:
        return dict(zip(output[0],output[1]))

def query_bitstream_table(bitstream_id):
    '''
    Returns a dict of values for the bitstream id
    '''
    sql = 'SELECT bitstream_format_id, name, size_bytes, checksum, checksum_algorithm, source, internal_id ' \
          'FROM bitstream WHERE bitstream_id = %d' % bitstream_id
    return dict_from_query(sql)

def query_bitstream_format(mimetype):
    sql = "SELECT bitstream_format_id FROM bitstreamformatregistry where mimetype = '%s'" % mimetype
    return dict_from_query(sql)

def update_bitstream_table(bitstream_id, large_file):
    format_dict = query_bitstream_format(large_file.mimetype)
    if format_dict is None:
        raise Exception("Critical: MIME type '%s' not found" % large_file.mimetype)
    format_id = format_dict['bitstream_format_id'] # stays a string
    sql = "UPDATE bitstream set size_bytes=%d, name='%s', source='%s' ,checksum='%s', bitstream_format_id=%s where bitstream_id = %d" % (
        large_file.size,
        large_file.name,
        large_file.name,
        large_file.md5(),
        format_id,
        bitstream_id
    )
    # TODO: More than just print the SQL
    print sql


def main():
    if check_write_access() == False:
        print "Cannot get write access to %s, check permissions or user account" % ASSETSTORE_PATH
        exit(-1)
    bitstream_id = get_bitstream_id()
    print "Bitstream ID: %d" % bitstream_id
    assetstore_path = get_assetstore_path(bitstream_id)
    largefile_path = get_largefile_path()
    dummyfile, largefile = None, None
    try:
        largefile = bitstream_file(largefile_path)
        largefile.check_mimetype()
        dummyfile = bitstream_file(assetstore_path)
    except BaseException as e:
        print "Unable to read file: %s" % e
        exit(-1)
    # Files are loaded
    # Verify the Dummy file is right
    verify_file(bitstream_id, dummyfile)

    # Update the bitstream table
    update_bitstream_table(bitstream_id, largefile)
    place_largefile(bitstream_id, largefile)

    # Verify the replaced file is right
    replaced_file = bitstream_file(assetstore_path)
    verify_file(bitstream_id, replaced_file)

if __name__ == '__main__':
    main()

