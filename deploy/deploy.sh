#!/usr/bin/env bash
PATH=lara
ssh ec2-user@$STAGING_SERVER "mkdir -p $PATH"
# rsync -rav -e ssh --exclude='.git/' --exclude=scripts/ --exclude='.travis.yml' --delete-excluded ./ ec2-user@$STAGING_SERVER:$PATH