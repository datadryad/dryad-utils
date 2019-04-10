#!/bin/bash

# Script to generate a list of (data package) item IDs to be indexed
# Assumes the PGHOST and PGPASSWORD environment variables are set.

echo Creating list of item IDs for indexing...

psql -qt -U dryad_app -d dryad_repo -c "select distinct item_id from item where (owning_collection=2 and in_archive=true) OR item_id in (select item_id from workflowitem where collection_id=2) OR item_id in (select item_id from workspaceitem where collection_id=2) order by item_id desc;" -o items.txt

echo List of items is in items.txt
