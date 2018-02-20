#! /bin/bash

# Database export for backup purposes
# Filename of the export includes the current minutes, so we can keep a few files around for history. 
# And when we copy the files to another machine, we can see whether we grabbed a file that was being created at the time it was copied, so may be incomplete.
#
# Usage: database-export.sh [-q]
# If the -q is present, the command will suppress output (for use with cron)


minutes=`date "+%M"`
hour=`date "+%H"`

if [ "$1" != "-q" ]
then
  echo Dumping to dryadDBlatest-${hour}_${minutes}.sql
fi
mkdir -p $HOME/databaseBackups/
/usr/bin/pg_dump -F c --host $DRYAD_DB_HOST >$HOME/databaseBackups/dryadDBlatest-${hour}_${minutes}.sql

if [ "$1" != "-q" ]
then
    echo Copying to dryadDBlatest.sql
fi
cp $HOME/databaseBackups/dryadDBlatest-${hour}_${minutes}.sql $HOME/databaseBackups/dryadDBlatest.sql
