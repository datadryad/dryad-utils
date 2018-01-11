#! /bin/bash

# This script lives on the ftp server and is invoked via crontab.

if [ ! -e ~/transfer_lock ];
then
	echo "transferring"
	touch ~/transfer_lock
	echo "rsyncing"
	rsync -rltgDvz --no-p --no-g --chmod=ug=rwx,o=rx /dryad-data/transfer/ /dryad-data/transfer-complete
	find /dryad-data/transfer -mindepth 2 -mmin +180 -exec rm -rf {} \;
	echo "aws sync"
	aws s3 sync /dryad-data/transfer-complete/ s3://dryad-ftp/ --delete
	python ~/dryad-utils/transfer_s3.py
	rm ~/transfer_lock
fi
chmod -R 777 /dryad-data/transfer-complete/
