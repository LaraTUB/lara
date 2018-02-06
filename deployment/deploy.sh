#!/bin/bash

echo ec2-user@$STAGING_SERVER

rsync -rav -e ssh --exclude='.git/' \
                  --exclude='.travis.yml' \
                  --exclude='app/app/instance/config.py' \
                  --exclude='app/app/instance/github_key.pem' \
                  --delete ./ ec2-user@$STAGING_SERVER:lara

ssh ec2-user@$STAGING_SERVER "cd lara && \
    docker-compose down && \
    docker-compose build && \
    docker-compose up"