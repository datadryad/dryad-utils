#!/usr/bin/env bash
#

DUMPFILE=$1
THREADS=4   # number of threads to spawn for update

if [[ "$DUMPFILE" == "" ]]; then
    echo "usage: importdb.sh DUMP_FILE"
    echo "Exiting."
    exit 1;
fi

if [[ ! -f "$DUMPFILE" ]]; then
    echo "File does not exist or is not a regular file: '$DUMPFILE'."
    echo "Exiting."
    exit 1
fi

dropdb dryad_repo
createdb -U dryad_app -E UNICODE dryad_repo
pg_restore -j $THREADS -d dryad_repo -U dryad_app $DUMPFILE 

