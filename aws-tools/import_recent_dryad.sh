#! /bin/bash


echo "grabbing latest from aws..."
/home/ubuntu/.local/bin/aws s3 cp s3://dryad-backup/databaseBackups/dryadDBlatest.sql $HOME/dryadDBlatest.sql 
import_pg_dump.sh $HOME/dryadDBlatest.sql

mkdir -p /opt/dryad/solr
/home/ubuntu/.local/bin/aws s3 sync s3://dryad-backup/solrBackups/ /opt/dryad/solr --delete
