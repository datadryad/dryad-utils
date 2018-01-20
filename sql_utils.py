#!/usr/bin/env python

# Methods for querying Dryad's database

__author__ = 'daisieh'

import re
import os

global DRYAD_DB

if 'DRYAD_DB_HOST' in os.environ:
	DRYAD_DB = os.environ['DRYAD_DB_HOST']
else:
	DRYAD_DB = ""	

def sql_query(sql):
	global DRYAD_DB
	host = ""
	if DRYAD_DB is not "":
		host = "--host " + DRYAD_DB
	return os.popen("psql %s -A -U dryad_app dryad_repo -c \"%s\"" % (host, sql))

def dict_from_query(sql):
    output = [line.strip().split('|') for line in sql_query(sql).readlines()]
    if len(output) <= 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        result = dict(zip(output[0],output[1]))
        return result
        
def list_from_query(sql):
    output = [line.strip().split('|') for line in sql_query(sql).readlines()]
    if len(output) == 1:
        return None
    else:
        resultkeys = output.pop(0)
        count = output.pop()[0]
        result = []
        for entry in output:
            result.append(dict(zip(resultkeys,entry)))
        return result

def get_field_id(name):
    parts = re.split('\.', name)
    schema = var_from_query("select metadata_schema_id from metadataschemaregistry where short_id = '%s'" % parts[0],'metadata_schema_id')
    if len(parts) > 2:
        field_id = var_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier = '%s'" % (schema, parts[1], parts[2]),'metadata_field_id')
    else:
        field_id = var_from_query("select metadata_field_id from metadatafieldregistry where metadata_schema_id=%s and element='%s' and qualifier is null" % (schema, parts[1]),'metadata_field_id')
    return field_id

def list_values_for_key(key,dict_list):
    result = []
    for item_dict in dict_list:
        val = None
        try:
            val = item_dict[key]
        except KeyError:
            val = 0
        result.append(val)
    return result

def rows_from_query(sql):
    output = [line.strip().split('|') for line in sql_query(sql).readlines()]
    if len(output) <= 2: # the output should have at least 3 lines: header, body rows, number of rows
        return None
    else:
        return output

def var_from_query(sql, param):
    dict = dict_from_query(sql)
    if dict is not None:
        return dict[param]
    return None

def execute_sql_query(sql):
    output = sql_query(sql).readlines()
    for line in output:
    	print line
