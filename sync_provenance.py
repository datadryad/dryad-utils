#!/usr/bin/env python

# Re-sync all packages with EZID. Takes two (or three) arguments:
# sync_provenance.py username password start_item
# start_item is the last item_id synced. If not specified, start from 0.

__author__ = 'daisieh'

import re
import sys
import doi_tool
from sql_utils import dict_from_query, rows_from_query

def get_field_id(name):
    parts = re.split('\.', name)
    schema = dict_from_query("select metadata_schema_id from metadataschemaregistry where short_id = '%s'" % parts[0])['metadata_schema_id']
    if len(parts) > 2:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier = '%s'" % (schema, parts[1], parts[2]))['metadata_field_id']
    else:
        field_id = dict_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier is null" % (schema, parts[1]))['metadata_field_id']
    return field_id
    
def main():
    username = sys.argv[1]
    password = sys.argv[2]
    cursor = 0
    if len(sys.argv) > 3:
        cursor = sys.argv[3]
    
    doi_field = get_field_id('dc.identifier')
    items = rows_from_query ("SELECT item.item_id AS item_id, mdv.text_value AS doi FROM item, metadatavalue AS mdv WHERE item.item_id = mdv.item_id AND item.in_archive = 't' AND mdv.metadata_field_id = %s AND mdv.text_value like 'doi%%' and item.item_id > %s order by item.item_id asc" % (doi_field, cursor))
    curr_item = ""
    labels = dict(zip(items[0], range(0,len(items[0]))))
    for item in items[1:-1]:
        item_id = item[labels['item_id']]
        item_doi = item[labels['doi']]
        if item_id == curr_item:
            continue
        curr_item = item_id
        print "%s\t%s" % (item_id, item_doi)
        m = re.search('DOI:(.*)', item_doi.upper())
        item_doi = 'doi:' + m.group(1)
        
        doi_tool.run_ezid(dict(doi=item_doi, is_blackout=False, action='update', username=username, password=password))

if __name__ == '__main__':
    main()

