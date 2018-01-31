PATH=lara
ssh ec2-user@$STAGING_SERVER "mkdir -p $PATH"
# rsync -rav -e ssh --exclude='.git/' --exclude='.travis.yml' --delete-excluded ./ ec2-user@$STAGING_SERVER:$PATH