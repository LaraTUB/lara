#!/bin/sh

ls .
ssh ec2-user@$STAGING_SERVER "mkdir -p lara"
ls ./

rsync -rav --exclude='.git/' --exclude='.travis.yml' --delete-excluded ./ ec2-user@$STAGING_SERVER:$PATH