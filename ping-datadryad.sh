#!/bin/sh

if [ -z "$1" ]
  then
  HOST_TO_QUERY=$HOSTNAME
  else
  HOST_TO_QUERY=$1
fi

echo "querying datadryad.org to see if it is pointing at $HOST_TO_QUERY"
while ping -c 1 datadryad.org | grep -q -m 2 $HOST_TO_QUERY 
do
    echo "datadryad.org still points at $HOST_TO_QUERY"
    sleep 10
done

