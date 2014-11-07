#!/usr/bin/env python
from sqlalchemy import Table, MetaData, create_engine
import sys, copy
from dryad_credentials import credentials

def get_engine():
  connection_string = "postgresql://%s:%s@%s:%d/%s" % (credentials['user'], credentials['password'], credentials['host'], credentials['port'], credentials['database'])
  print 'connecting to %s' % credentials['host']
  engine = create_engine(connection_string)
  return engine

# epersongroup2eperson
# tasklistitem
# Get the current curators

def get_curator_group(conn):
  query = 'select eperson_group_id from epersongroup where name = \'Curators\''
  results = conn.execute(query)
  for result in results:
    return result['eperson_group_id']

def get_admin_group(conn):
  query = 'select eperson_group_id from epersongroup where name = \'Administrator\''
  results = conn.execute(query)
  for result in results:
    return result['eperson_group_id']

def get_members(conn, group_id):
  query = 'select eperson_id from epersongroup2eperson where eperson_group_id = %d' % group_id
  results = conn.execute(query)
  return (result['eperson_id'] for result in results)

# insert into tasklistitem values (getnextid('tasklistitem'), 7147,'dryadAcceptEditReject','claimAction',20986,'default');

def generate_tasklistitem_row(eperson_id, step, action, workflow_item_id):
  return 'insert into tasklistitem values (getnextid(\'tasklistitem\'), %d,\'%s\',\'%s\',%d,\'default\')' % (eperson_id, step, action, workflow_item_id)

def get_tasklistitem_rows(conn, workflow_item_id):
  query = 'select * from tasklistitem where workflow_item_id = %d' % (workflow_item_id,)
  results = conn.execute(query)
  return results

# When an item is unclaimed, there are lots of rows in tasklistitem for it and no rows in taskowner for it.
# When claimed, there are no rows in tasklistitem, but one in taskowner

# Start by getting the distinct workflow ids in tasklistitem
  # These should be all te things available to curators
# then examine each one
  # if the eperson id is in the curators list, good
  # if it's not, remove it
  # if a curator is not in the list, add it.

def get_workflow_item_id_for_doi(conn, doi):
  query = 'select wfi.workflow_id as workflow_item_id from workflowitem wfi, metadatavalue mdv where wfi.item_id = mdv.item_id and mdv.metadata_field_id = 17 and mdv.text_value = \'%s\'' % (doi,)
  results = conn.execute(query)
  return list(result['workflow_item_id'] for result in results)[0]

def get_distinct_workflow_item_ids(conn):
  query = 'select distinct(workflow_item_id) as workflow_item_id from tasklistitem where action_id = \'claimAction\''
  workflow_item_ids = []
  results = conn.execute(query)
  return (result['workflow_item_id'] for result in results)

def insert_tasklistitem_row(conn, eperson_id, tasklistitem):
  step = tasklistitem['step_id']
  action = tasklistitem['action_id']
  workflow_item_id = tasklistitem['workflow_item_id']
  row = generate_tasklistitem_row(eperson_id, step, action, workflow_item_id)
  print row
#  conn.execute(row)
  
def delete_eperson_from_tasklistitem(conn, eperson_id):
  query = 'delete from tasklistitem where eperson_id = %d' % (eperson_id,)
  print query

def generate_tasklistitem_prototype(workflow_item_id):
  return {'step_id' : 'dryadAcceptEditReject', 'action_id' : 'dryadAcceptEditRejectAction', 'workflow_item_id' : workflow_item_id}

def fix_taskowners(doi):
  if doi is None:
    raise 'Must provide a DOI'
    return
  engine = get_engine()
  with engine.connect() as conn:
    curator_group_id = get_curator_group(conn)
    curator_ids = list(get_members(conn, curator_group_id))
    if doi is None:
      workflow_item_ids = list(get_distinct_workflow_item_ids(conn))
    else:
      workflow_item_ids = [get_workflow_item_id_for_doi(conn, doi)]
    # Global list of epersons that are not curators and should be removed from
    # all tasklistitem rows
    epersons_to_remove = list() 
    for workflow_item_id in workflow_item_ids:
      print workflow_item_id
      tasklistitems = get_tasklistitem_rows(conn, workflow_item_id)
      tasklistitem_prototype = None
      epersons_to_add = copy.copy(curator_ids)
      for tasklistitem in tasklistitems:
        if tasklistitem_prototype is None:
          tasklistitem_prototype = tasklistitem
        eperson_id = tasklistitem['eperson_id']
        if eperson_id in curator_ids:
          # This row is valid, eperson is a valid curator
          epersons_to_add.remove(eperson_id)
        else:
          # the person referenced by this tasklistitem is not currently a curator
          epersons_to_remove.append(eperson_id)
      if tasklistitem_prototype is None:
        print 'no tasklistitems for doi %s, generating prototype' % (doi)
        tasklistitem_prototype = generate_tasklistitem_prototype(workflow_item_id)
      for eperson_id in set(epersons_to_add):
        insert_tasklistitem_row(conn, eperson_id, tasklistitem_prototype)
    epersons_to_remove = set(epersons_to_remove)
    for eperson_id in epersons_to_remove:
      delete_eperson_from_tasklistitem(conn, eperson_id)

if __name__ == '__main__':
  if len(sys.argv) > 1:
    doi = sys.argv[1]
  else:
    doi = None
  fix_taskowners(doi)

