#!/usr/bin/env python

__author__ = 'daisie'

import os
from sql_utils import list_from_query, list_values_for_key

def query_bitstream_table(bitstream_id):
    '''
    Returns a dict of values for the bitstream id
    '''
    sql = 'SELECT bitstream_format_id, name, size_bytes, checksum, checksum_algorithm, source, internal_id ' \
          'FROM bitstream WHERE bitstream_id = %d' % int(bitstream_id)
    return list_from_query(sql).pop(0)

def get_bitstream_for_file(file_doi):
    '''
    Returns a list of dicts: each one has a file_id and a list of associated bitstream ids.
    '''
    sql = "select item_id from metadatavalue where text_value='%s'" % (file_doi)
    file_id_list = list_values_for_key('item_id',list_from_query(sql))
    bitstream_id_list = []
    # for each file id:
    for file_id in file_id_list:
        sql = 'select * from item2bundle where item_id = %d' % int(file_id)
        bundles = list_from_query(sql)
        if len(bundles) > 0:
            bundle_id = bundles[0]['bundle_id']
            sql = 'select * from bundle2bitstream where bundle_id = %d' % int(bundle_id)
            bitstreams = list_values_for_key('bitstream_id',list_from_query(sql))
            filebitstream = {'file_id':file_id,'bitstreams':bitstreams}
            bitstream_id_list.append(filebitstream)
    return bitstream_id_list

def query_bitstream_format(mimetype):
    sql = "SELECT bitstream_format_id FROM bitstreamformatregistry where mimetype = '%s'" % mimetype
    return list_from_query(sql).pop(0)
    
def insert_resourcepolicy(bitstream_id):
	sql = "INSERT INTO resourcepolicy (policy_id, resource_type_id, resource_id, action_id, eperson_id, epersongroup_id, start_date, end_date) VALUES (nextval('resourcepolicy_seq'), 0, %d, 0, NULL, 0, NULL, NULL)" % int(bitstream_id)
	return list_from_query(sql)


def main():
    file_doi = raw_input('Enter the file DOI: ')
    bitstream_list = get_bitstream_for_file(file_doi)
    for file in bitstream_list:
        file_id = file['file_id']
        bitstreams = file['bitstreams']
        for bitstr in bitstreams:
            bitstream_dict = query_bitstream_table(bitstr)
            insert_resourcepolicy(bitstr)



if __name__ == '__main__':
    main()

