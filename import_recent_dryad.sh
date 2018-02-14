#! /bin/bash


echo "grabbing latest from aws..."
aws s3 cp s3://dryad-backup/databaseBackups/dryadDBlatest.sql $HOME/dryadDBlatest.sql 
mkdir -p /opt/dryad/solr
aws s3 sync s3://dryad-backup/solrBackups/ /opt/dryad/solr --delete
