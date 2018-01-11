#!/usr/bin/env python

# It only works on a single item_id, and requires sqlalchemy
#
# delete_item.py item_id
#
# It connects to the Postgres database with parameters specified in dryad_credentials.py.
# This script does not exist in the repo, you should create it:
#
# credentials = {
#  'user': 'username',
#  'password': 'password',
#  'host': '127.0.0.1',
#  'port': 6543,
#  'database': 'database',
#  }
#
# To use this with a remote server, create an SSH tunnel, e.g.:
# ssh -L 6543:127.0.0.1:5432 username@host.com

from sqlalchemy import Table, MetaData, create_engine
import sys, copy
import re
from dryad_credentials import credentials
from string import Template

def get_engine():
  connection_string = "postgresql+psycopg2://%s:%s@/%s" % (credentials['user'], credentials['password'], credentials['database'])
  engine = create_engine(connection_string)
  return engine

def get_tasklistitem_rows(conn, workflow_item_id):
  query = 'select * from tasklistitem where workflow_item_id = %d' % (workflow_item_id,)
  results = conn.execute(query)
  return results

def get_workflow_item_id_for_doi(conn, doi):
  query = 'select wfi.workflow_id as workflow_item_id from workflowitem wfi, metadatavalue mdv where wfi.item_id = mdv.item_id and mdv.metadata_field_id = 17 and mdv.text_value = \'%s\'' % (doi,)
  results = conn.execute(query)
  return list(result['workflow_item_id'] for result in results)[0]

def get_dois_for_item_id(conn, item_id):
  query = 'select text_value as doi from metadatavalue where metadata_field_id = 17 and item_id=%s' % (item_id)
  results = conn.execute(query)
  return list(result['doi'] for result in results)
  
def get_bundles_for_item_id(conn, item_id):
  query = 'select bundle_id as bundle_ids from item2bundle where item_id in (select part.item_id from metadatavalue part, metadatavalue package where part.metadata_field_id in (17,42) and package.metadata_field_id = 17 and part.text_value = package.text_value and package.item_id = %s)' % (item_id)
  results = conn.execute(query)
  return list(result['bundle_ids'] for result in results)

def get_bitstreams_for_item_id(conn, item_id):
  query = 'select bitstream_id as bitstream_ids from bundle2bitstream where bundle_id in (select bundle_id from item2bundle where item_id in (select part.item_id from metadatavalue part, metadatavalue package where part.metadata_field_id in (17,42) and package.metadata_field_id = 17 and part.text_value = package.text_value and package.item_id = %s))' % (item_id)
  results = conn.execute(query)
  return list(result['bitstream_ids'] for result in results)

def delete_haspart_metadata(conn, doi):
  query = 'DELETE FROM metadatavalue where metadata_field_id = 44 and text_value like \'%s\'' % (doi)
  results = conn.execute(query)
  print query

# DELETE FROM doi WHERE doi_suffix='<doi_suffix>';
def delete_doi(conn, doi):
  matcher = "doi:\d\d\.\d+\/(.+)"
  doi_suffix_match = re.match(matcher, doi)
  doi_suffix = ""
  if matcher != None:
    doi_suffix = doi_suffix_match.group(1)  
  query = 'DELETE FROM doi WHERE doi_suffix= \'%s\'' % (doi_suffix)
  results = conn.execute(query)
  print query

def delete_item(item_id):
  if item_id is None:
    raise 'Must provide a item_id'
    return
  engine = get_engine()
  with engine.connect() as conn:
    dois = get_dois_for_item_id(conn, item_id)
    bundle_ids = ','.join(str(b) for b in get_bundles_for_item_id(conn, item_id))
    bitstream_ids = ','.join(str(b) for b in get_bitstreams_for_item_id(conn, item_id))
    for doi in dois:
       delete_haspart_metadata(conn, doi)
       delete_doi(conn, doi)
    s = Template('DELETE FROM item2bundle WHERE item_id= $item AND bundle_id in ($bundleids)')
    query = s.substitute(item=item_id, bundleids=bundle_ids)
    results = conn.execute(query)

    s = Template('DELETE FROM bundle2bitstream WHERE bundle_id in ($bundleids) and bitstream_id in ($bitstreamids)')
    query = s.substitute(bundleids=bundle_ids,bitstreamids=bitstream_ids)
    results = conn.execute(query)

    s = Template('DELETE FROM bundle WHERE bundle_id in ($bundleids)')
    query = s.substitute(bundleids=bundle_ids)
    results = conn.execute(query)

    s = Template('DELETE FROM most_recent_checksum where bitstream_id in ($bitstreamids)')
    query = s.substitute(bitstreamids=bitstream_ids)
    results = conn.execute(query)

    s = Template('DELETE FROM bitstream WHERE bitstream_id in ($bitstreamids)')
    query = s.substitute(bitstreamids=bitstream_ids)
    results = conn.execute(query)

       
if __name__ == '__main__':
  if len(sys.argv) > 1:
    item_id = sys.argv[1]
  else:
    item_id = None
  delete_item(item_id)

