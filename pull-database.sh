#!/usr/bin/env bash

if [ -z $1 ]; then
    echo "Usage: pull-database.sh <ec2-privatekey>";
else
    scp -i $1 ec2-user@ec2-54-89-185-46.compute-1.amazonaws.com:app/app/instance/lara.db ./app/instance/lara.db
fi