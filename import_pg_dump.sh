#!/usr/bin/env bash
#

DUMPFILE=$1
DBHOST=$2
THREADS=4   # number of threads to spawn for update

if [[ "$DUMPFILE" == "" ]]; then
    echo "usage: importdb.sh DUMP_FILE DBHOST"
    echo "Exiting."
    exit 1;
fi

if [[ ! -f "$DUMPFILE" ]]; then
    echo "File does not exist or is not a regular file: '$DUMPFILE'."
    echo "Exiting."
    exit 1
fi

if [[ "$DBHOST" == "" ]]; then
	DBHOST=$DRYAD_DB_HOST
fi

if [[ "$DBHOST" == "" ]]; then
	psql -U dryad_app -d dryad_repo -c "select pg_terminate_backend(pid) from pg_stat_activity where datname='dryad_repo'"
	dropdb dryad_repo
	createdb -U dryad_app -E UNICODE dryad_repo
	pg_restore -j $THREADS -d dryad_repo -U dryad_app $DUMPFILE 
fi

if [[ "$DBHOST" != "" ]]; then
	psql --host $DBHOST -U dryad_app -d dryad_repo -c "select pg_terminate_backend(pid) from pg_stat_activity where datname='dryad_repo'"
	dropdb --host $DBHOST -U dryad_app dryad_repo
	createdb --host $DBHOST -U dryad_app -E UNICODE dryad_repo
	pg_restore --host $DBHOST -j $THREADS -d dryad_repo -U dryad_app $DUMPFILE 
fi
