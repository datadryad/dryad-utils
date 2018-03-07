#! /bin/bash

INSTANCE_NAME=$1

crontab -l | diff - /home/ubuntu/crontab.txt

if [[ $? -ne 0 ]]; then
	crontab -l > /home/ubuntu/crontab.txt
	/home/ubuntu/.local/bin/aws s3 cp /home/ubuntu/crontab.txt s3://dryad-backup/crontabs/$INSTANCE_NAME.txt
fi
