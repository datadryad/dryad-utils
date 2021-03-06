Tools to facilitate migrating large groups of items.

- `dash-migration/dash_make_list_size.sh` -- make a list of Handles for Dryad data packages, with their associated size and version number. This list may besorted to allowtransfers in order of size.
- `dash-migration/dash_make_list_workflow.sh` -- make a list of Handles for Dryad data packages, for items in the curation workflow
- `dash-migration/dash_make_list_workspace.sh` -- make a list of Handles for Dryad data packages, for items in the user workspace
- `dash-migration/dash_make_list_transferred.sh` -- make a list of Handles for Dryad data packages, contianing items that have been transferred to DASH but not yet marked as being processed by Merritt
- `dash-migration/dash_transfer.sh` -- transfer a single data package to DASH
- `dash-migration/dash_transfer_many.sh` -- given a list of Handles, transfer data packages to DASH
- `dash-migration/dash_monitor.sh` -- monitor an item in DASH to determine whether it has been successfully processed by Merritt
- `dash-migration/dash_monitor_many.sh` -- monitor a list of items to determine whether they have been successfully processed by Merritt

To create a list of handles ordered by size, while respecting the version history:
1. set the log4j-dspace-cli.properties to have `curate=ERROR`
2. `dash_make_list_size.sh`
3. `sort -t"," -k3 -k2rn -k1  dashList.log >dashListSorted.log`
4. `sed -e 's/,.*//' dashListSorted.log >dashListToTransfer.log`
5. set the log4j-dspace-cli.properties to have `curate=DEBUG`
	  
