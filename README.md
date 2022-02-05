# zoom-archiver

## Description

The Zoom Archiver is a process designed to run periodically out of AWS's Elastic Container Service (ECS). The process is setup to run based on a CRON schedule provided to the ECS cluster it will run out of and collect all Zoom videos in cloud storage for provided user accounts maintained in a google sheet which are about to be automatically deleted out of the Zoom cloud due to those videos being of a certain age set within the Zoom cloud platform.


The process involves many different AWS services, and here is where each can be found:
- ECS, where the process is run inside your chosen cluster
- Elastic Container Registry, where the docker image for the process is stored
- IAM, where the permissions policies for the process are stored as `zoomarchiver-task-role` and `zoomarchiver-task-execution-role`
- Secrets Manager, where the Zoom, Google API, and Mailchimp secrets are stored
- DynamoDB, where the users and files tables are stored
- CloudWatch, where the process logs to the log group `zoomarchiver`
- S3, where the process ultimately stores the downloaded Zoom files


check out this great tutorial I used to work out this process:
https://aws.amazon.com/blogs/compute/securing-credentials-using-aws-secrets-manager-with-aws-fargate/


## requirements

1. an AWS account with s3, DynamoDB, ECS, ECR, Secrets Manager, CloudWatch, and IAM enabled
1. a Mailchimp account
1. a Google service account with credentials JSON file, and personal Google account
1. Two DynamoDB tables initialised, one for users and one for files. You should use "email" as the main index of the users table, and "recording_id" as the main index of the files table, both of these values are strings.
1. An S3 bucket to store your files

**ONCE YOU HAVE ALL THESE IN PLACE YOU SHOULD BE ABLE TO FILL OUT zoomarchiver-task.json AND zoomarchiver-iam-policy-task-role.json**

## build instructions

1. install docker and aws-cli locally
1. add a profile to your `credentials` file located at `~/.aws/credentials` for your current SSO credentials, make sure that when you are entering the commands below which call for the argument `--profile MYPROFILE` you substitute MYPROFILE for the profile name you have chosen, substitute AWS_ID for your AWS account ID, and substitute MY_REG with your AWS region
1. in terminal navigate to project root
1. run `aws ecr get-login-password --region us-east-1 --profile MYPROFILE | docker login --username AWS --password-stdin AWS_ID.dkr.ecr.MY_REG.amazonaws.com` to log into aws from the command line to log docker into ECR
1. run `aws iam create-role --region MY_REG --role-name zoomarchiver-task-role --assume-role-policy-document file://aws/ecs-task-role-trust-policy.json --profile MYPROFILE` to create iam task role
1. run `aws iam create-role --region MY_REG --role-name zoomarchiver-task-execution-role --assume-role-policy-document file://aws/ecs-task-role-trust-policy.json --profile MYPROFILE` to create iam task execution role
1. run `aws iam put-role-policy --region MY_REG --role-name zoomarchiver-task-role --policy-name zoomarchiver-iam-policy-task-role --policy-document file://aws/zoomarchiver-iam-policy-task-role.json --profile MYPROFILE` to add dynamo and s3 permissions to the iam task role
1. run `aws iam put-role-policy --region MY_REG --role-name zoomarchiver-task-execution-role --policy-name zoomarchiver-iam-policy-task-execution-role --policy-document file://aws/zoomarchiver-iam-policy-task-execution-role.json --profile MYPROFILE` to add log and secret manager permissions to the iam task execution role
1. run `aws ecs register-task-definition --region us-east-1 --cli-input-json file://aws/zoomarchiver-task.json --profile MYPROFILE` to create task definition role. This file has all environment settings in it.
1. run `aws logs create-log-group --log-group-name zoomarchiver --region MY_REG --profile MYPROFILE` to create the log group for the process
1. run `docker build -t zoomarchiver .` to build docker image locally
1. run `docker tag zoomarchiver:latest AWS_ID.dkr.ecr.us-east-1.amazonaws.com/zoomarchiver:latest` to tag the image as latest
1. run `docker push AWS_ID.dkr.ecr.MY_REG.amazonaws.com/zoomarchiver:latest` to push image into AWS ECR

## deployment instructions

1. In browser, go to the AWS ECS console.
1. Choose Clusters from the right hand menu and then click into your chosen cluster.
1. Click on the Scheduled Tasks tab and then click Create below.
1. Fill out each field, but make sure to choose: Cron Expression for Schedule rule type, FARGATE for Launch type, at least 1 subnet which can talk out, create a new Security group, and ENABLED for Auto-assign public IP.
1. Click Create below and now the process will run based on the Cron expression you provided above. 
