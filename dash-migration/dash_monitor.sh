#!/bin/bash

# Script to mointor items that have been transfered from Dryad to DASH 

# Usage: dash_monitor.sh <handle-to-monitor>
# If no handle is supplied, use the default of "the data packages collection"

if [ -z "$1" ]
then
    HANDLE="10255/3"
else
    HANDLE="$1"
fi

/opt/dryad/bin/dspace curate -v -t dashmonitor -i $HANDLE -r -
