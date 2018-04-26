#! /bin/bash

# This script lives on the ftp server and is invoked via crontab.

if [ ! -e ~/transfer_lock ];
then
	date
	echo "transferring"
	touch ~/transfer_lock
	echo "rsyncing"
	# Find the files in transfer that were modified no sooner than 1 hour ago; 
	# rsync those to the transfer-complete folder and remove from source.
	find /dryad-data/transfer -mindepth 2 -mmin +60 -printf %P\\0 \
	| rsync -rltgDzi --no-p --no-g --chmod=ug=rwx,o=rx --remove-source-files --files-from=- --from0 /dryad-data/transfer/ /dryad-data/transfer-complete
	echo "aws sync"
	/usr/local/bin/aws s3 sync /dryad-data/transfer-complete/ s3://dryad-ftp/ --delete
	echo "adding md5 tags"
	/usr/bin/python ~/dryad-utils/transfer_s3.py
	echo "done"
	rm ~/transfer_lock
fi
