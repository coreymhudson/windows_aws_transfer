This software isn't super sophisticated. It allows you to use AWS credentials to upload directly to an S3 bucket, without having to have AWS CLI.

You will need 4 items:
1) An AWS Access Key ID
2) An AWS Secret Access Key - you can really only generate this once and this uploader won't save it, so have it saved somewhere else
3) The location: default is us-east-1
4) The bucket name

The permissions will have to be established on the AWS management console side. This will not help with that.
