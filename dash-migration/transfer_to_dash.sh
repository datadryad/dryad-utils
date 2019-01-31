# Usage: transfer_to_dash.sh <handle-to-transfer>
# If no handle is supplied, use the default of "the data packages collection"

if [ -z "$1" ]
then
    HANDLE="10255/3"
else
    HANDLE="$1"
fi

/opt/dryad/bin/dspace curate -v -t transfertodash -i $HANDLE -r -
