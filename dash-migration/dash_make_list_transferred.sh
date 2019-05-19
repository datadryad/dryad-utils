# Usage: dash_make_transferred_list.sh

# Makes a list of the items that have been transferred to DASH but not yet
# marked as being stored in Merritt.

echo Creating list of items to transfer stats to DASH...

psql -qt -U dryad_app -d dryad_repo -c "select handle from handle where resource_id in (select item_id from metadatavalue where metadata_field_id =170 and item_id not in (select item_id from metadatavalue where metadata_field_id=171));" -o items.txt

echo List of items is in items.txt

