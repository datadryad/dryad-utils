#!/bin/bash

# Allows the secundus database to alternate between two on-demand
# Amazon RDS machines, flip and flop. 

# Requires a file, /home/ec2-user/.current_db, that contains the name of the current db, 
# either flip or flop.

# This script assumes that $CURRENT_DB is currently being used, and it will switch  
# the database to $NEXT_DB.

CURRENT_DB=`head -n 1 /home/ec2-user/.current_db`

if [ $CURRENT_DB = 'flip' ]
then
        NEXT_DB='flop'
else
        NEXT_DB='flip'
fi

echo Current dryad database is $CURRENT_DB
echo Rebuilding the dryad database with $NEXT_DB...

echo $PGPASSWORD

# create a new RDS
aws rds create-db-instance --db-name dryad_repo --db-instance-identifier secundus-db-$NEXT_DB --allocated-storage 50 --db-instance-class db.t2.small --engine postgres --master-username dryad_app --master-user-password $PGPASSWORD --publicly-accessible --vpc-security-group-ids "sg-77d83c0b"

# ensure the new hostname is in the .pgpass file (it is for flip and flop)

# wait for the database creation to complete
sleep 300

# populate the new database from a recent backup of production (change the hostname)
pg_restore -j 4 --host=secundus-db-$NEXT_DB.co33oyzjqasf.us-east-1.rds.amazonaws.com -d dryad_repo -U dryad_app /opt/dryad-data/databaseBackups/dryadDBlatest-00_30.sql

# update the bin/pc script to use the new name
cp /home/ec2-user/database-switch/pc.$NEXT_DB /home/ec2-user/bin/pc

# update the .m2/settings.xml
cp /home/ec2-user/database-switch/maven-settings.$NEXT_DB /home/ec2-user/.m2/settings.xml

# redeploy-dryad.sh
/home/ec2-user/bin/redeploy-dryad.sh

# delete old instance of the database
aws rds delete-db-instance --db-instance-identifier secundus-db-$CURRENT_DB --skip-final-snapshot

# poke the SOLR index to ensure it is updated
sudo /opt/dryad/bin/dspace update-discovery-index -f -i 172834

# update the current_db file with the new current db
echo $NEXT_DB > /home/ec2-user/.current_db

echo
echo     ====  REBUILD SUCCEEDED ====
echo
