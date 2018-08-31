#!/bin/bash

# Query postgres in a way that allows easy processing of the results in a bash script
psql --host=$DRYAD_DB_HOST \
   --port=5432 \
   --username=dryad_app  \
   --dbname=dryad_repo \
   -t \
   --no-align \
   --field-separator $'\t'\
   --quiet \
   -c "$1"
