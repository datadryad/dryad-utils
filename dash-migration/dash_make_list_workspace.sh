#!/bin/bash

# Script to generate a list of items to be transferred to DASH
# Assumes the PGHOST and PGPASSWORD environment variables are set.

echo Creating list of items to transfer to DASH...

psql -qt -U dryad_app -d dryad_repo -c "select handle from handle where resource_id in (select item_id from workspaceitem where collection_id=2 and item_id in (select item_id from item where last_modified > '2019-01-01')) order by handle_id desc;" -o items.txt

echo List of items is in items.txt
