#!/usr/bin/env python

# It only works on a single doi, and requires sqlalchemy
#
# process_hamr.py doi:10.5061/dryad.xxxxx
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
import os
import re
from dryad_credentials import credentials

def get_engine():
  connection_string = "postgresql://%s:%s@%s:%d/%s" % (credentials['user'], credentials['password'], credentials['host'], credentials['port'], credentials['database'])
  print 'connecting to %s' % credentials['host']
  engine = create_engine(connection_string)
  return engine

def get_collection_id_for_doi(conn, doi):
#  query = 'select wfi.workflow_id as workflow_item_id from workflowitem wfi, metadatavalue mdv where wfi.item_id = mdv.item_id and mdv.metadata_field_id = 17 and mdv.text_value = \'%s\'' % (doi,)
  query = 'select mdv_hdl.text_value as handle from metadatavalue mdv_doi, metadatavalue mdv_hdl where mdv_doi.item_id=mdv_hdl.item_id and (mdv_doi.metadata_field_id=17 and mdv_doi.text_value=\'%s\') and mdv_hdl.metadata_field_id=25' % (doi,)
  results = conn.execute(query)
  return list(result['handle'] for result in results)[0]

def perform_hamr_task(doi):
  item_id = 0
  if doi is None:
    raise 'Must provide a DOI'
    return
  engine = get_engine()
  with engine.connect() as conn:
    collection_id = [get_collection_id_for_doi(conn, doi)][0]
  #http://hdl.handle.net/10255/dryad.35555
  match = re.search('(10255\/dryad\.\d+)', collection_id)
  if match:
    collection_id = match.group(0)  
    print collection_id
  else:
    print "no match"
    
if __name__ == '__main__':
  if len(sys.argv) > 1:
    doi = sys.argv[1]
  else:
    doi = None
  perform_hamr_task(doi)
