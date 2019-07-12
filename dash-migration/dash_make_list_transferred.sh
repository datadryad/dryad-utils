# Usage: dash_make_list_transferred.sh

# Makes a list of the items that have been transferred to DASH 

export DASH_TRANSFER_FIELD="170"
export DASH_STORED_FIELD="171"

echo Creating list of items...

psql -qt -U dryad_app -d dryad_repo -c "select handle from handle where resource_id in (select item_id from metadatavalue where metadata_field_id = $DASH_TRANSFER_FIELD);" -o items.txt

echo List of items is in items.txt

