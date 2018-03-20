#! /bin/bash

# Loads a backed-up crontab for INSTANCE_NAME from dryad-backup/crontabs at S3. 
# Takes a single argument, the instance name.

INSTANCE_NAME=$1

crontab -l | diff - /home/ubuntu/crontab.txt &>/dev/null

if [[ $? -ne 0 ]]; then
	crontab -l > /home/ubuntu/crontab.txt
	/home/ubuntu/.local/bin/aws s3 cp /home/ubuntu/crontab.txt s3://dryad-backup/crontabs/$INSTANCE_NAME.txt
fi
