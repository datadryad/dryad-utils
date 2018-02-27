#!/bin/sh

# Checks to see if datadryad.org still points at the specified host. Takes an optional second argument for the port number.

if [ -z "$1" ]
  then
  HOST_TO_QUERY=$HOSTNAME
  else
  HOST_TO_QUERY=$1
fi

if [ -z "$2" ]
  then
  PORT=8080
  else
  PORT=$2
fi

echo "querying datadryad.org to see if it is pointing at $HOST_TO_QUERY"
while nc -vz $HOST_TO_QUERY $PORT 2>&1 | grep -q succeeded
do
    echo "datadryad.org still points at $HOST_TO_QUERY"
    sleep 10
done

