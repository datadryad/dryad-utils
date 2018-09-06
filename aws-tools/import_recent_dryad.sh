#! /bin/bash

# Usage: import_recent_dryad.sh [skipdb]
#
# If the 'skipdb' parameter is present, the database is not updated

echo "grabbing latest from aws..."

if [ "$1" != "skipdb" ]
then
   echo "Database..."
   /home/ubuntu/.local/bin/aws s3 cp s3://dryad-backup/databaseBackups/dryadDBlatest.sql $HOME/dryadDBlatest.sql 
   import_pg_dump.sh $HOME/dryadDBlatest.sql
fi

echo "SOLR..."
mkdir -p /opt/dryad/solr
/home/ubuntu/.local/bin/aws s3 sync s3://dryad-backup/solrBackups/ /opt/dryad/solr --delete
