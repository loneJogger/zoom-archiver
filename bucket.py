# imports
import os
import boto3
import boto3.session
import logToCon

# upload a file to an s3 bucket
def upload(file_name, bucket_name, user):

    session = boto3.session.Session()
    s3 = session.client('s3')
    a = user['email']['S'].split('@')
    username = a[0]
    try:
        res = s3.upload_file(file_name, bucket_name, '{}/{}'.format(username, file_name))
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    return True
