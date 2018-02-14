#!/bin/bash

echo ec2-user@$STAGING_SERVER

rsync -rav -e ssh --exclude='.git/' \
                  --exclude='instance/*' \
                  --delete ./ ec2-user@$STAGING_SERVER:lara

ssh ec2-user@$STAGING_SERVER "cd lara && \
    docker-compose down && \
    docker-compose build && \
    docker-compose up -d"