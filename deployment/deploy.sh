#!/bin/sh

ssh ec2-user@$STAGING_SERVER "mkdir -p lara"
rsync -rav -e ssh --exclude='.git/' --exclude='.travis.yml' --delete-excluded ./ ec2-user@$STAGING_SERVER:$PATH