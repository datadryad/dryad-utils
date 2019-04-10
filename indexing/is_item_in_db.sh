#!/bin/bash

# Script to generate a list of (data package) item IDs to be indexed
# Assumes the PGHOST and PGPASSWORD environment variables are set.

echo "Is $1 an item in the database?"

psql -qt -U dryad_app -d dryad_repo -c "select * from item where item_id=$1;"
psql -qt -U dryad_app -d dryad_repo -c "select * from workflowitem where item_id=$1;"
psql -qt -U dryad_app -d dryad_repo -c "select * from workspaceitem where item_id=$1;"

