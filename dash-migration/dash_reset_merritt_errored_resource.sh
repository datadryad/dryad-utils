#!/bin/bash

# Script to reset the status of a resource that has errored in Merritt and needs to be resubmitted to Merritt.

# Usage: dash_reset_merritt_errored_resource.sh <resource-id>

~/bin/mc -e "update stash_engine_resource_states set resource_state ='processing' where resource_id=$1;"
~/bin/mc -e "update stash_engine_repo_queue_states set state='enqueued' where resource_id=$1 and state='processing';"
~/bin/mc -e "update stash_engine_repo_queue_states set state='rejected_shutting_down' where resource_id=$1 and state='errored';"
