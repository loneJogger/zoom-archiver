# imports
import os
import boto3
import logToCon

# get all entries in a table
def getAll(table_name):

    dynamoDB = boto3.client('dynamodb', region_name='us-east-1')
    try:
        response = dynamoDB.scan(TableName=table_name)
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        try:
            response = dynamoDB.scan(TableName=table_name, ExclusiveStartKey=response['LastEvaluatedKey'])
        except RuntimeError as e:
            logToCon.log.error(e)
            return False
        data.extend(response['Items'])
    logToCon.log.info('all entries in {} successfully retrieved.'.format(table_name))
    return data

# get active users in users table
def getActive(table_name):

    dynamoDB = boto3.client('dynamodb', region_name='us-east-1')
    try:
        response = dynamoDB.scan(TableName=table_name)
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        try:
            response = dynamoDB.scan(TableName=table_name, ExclusiveStartKey=response['LastEvaluatedKey'])
        except RuntimeError as e:
            logToCon.log.error(e)
            return False
        data.extend(response['Items'])
    res = []
    for entry in data:
        if entry['active']['BOOL'] == True:
            res.append(entry)
    logToCon.log.info('all active users successfully retrieved.')
    return res

# compare table to sheet: if entry from sheet is not in table it is added,
# if entry from sheet is in table do nothing, if entry from table is not in
# sheet set entry in table to deactive
def compareSheetToTable(sheet, table):

    tableList = []
    for entry in table:
        tableList.append(entry['email']['S'])
    changes = []
    for email in sheet:
        if email not in tableList:
            changes.append({
                "email" : email,
                "type" : "add"
            })
    for email in tableList:
        if email not in sheet:
            changes.append({
                "email" : email,
                "type" : "deactivate"
            })
    logToCon.log.info('DB changes staged...')
    return changes

# write changes to table
def writeChanges(table_name, changes):

    dynamoDB = boto3.client('dynamodb', region_name='us-east-1')
    for change in changes:
        if change['type'] == "add":
            try:
                dynamoDB.put_item(
                    TableName=table_name,
                    Item={
                        'email' : {'S': change['email']},
                        'active' : {'BOOL': True}
                    }
                )
            except RuntimeError as e:
                logToCon.log.error(e)
                return False
        elif change['type'] == "deactivate":
            try:
                dynamoDB.update_item(
                    TableName=table_name,
                    Key={
                        'email' : {'S': change['email']}
                    },
                    UpdateExpression='SET active = :val',
                    ExpressionAttributeValues={
                        ':val' : {'BOOL': False}
                    }
                )
            except RuntimeError as e:
                logToCon.log.error(e)
                return False
    logToCon.log.info('DB update complete!')

# write that a file has been successfully achived to the table
def writeCompletedFile(table_name, file_data, file_name, user):

    dynamoDB = boto3.client('dynamodb', region_name='us-east-1')
    try:
        dynamoDB.put_item(
            TableName=table_name,
            Item={
                'recording_id': {'S': file_data['recording_id']},
                'name': {'S': file_name},
                'url': {'S': file_data['url']},
                'type': {'S': file_data['type']},
                'time': {'S': file_data['time']},
                'desc': {'S': file_data['desc']},
                'owner': {'S': user['email']['S']}
            }
        )
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    logToCon.log.info('entry for {} has been written to {}.'.format(file_name, table_name))

# checks to see if the files table has an entry for the current file
def checkForFile(table_name, file_data):

    downloaded = getAll(table_name)
    for entry in downloaded:
        if entry['recording_id'] == file_data['recording_id']:
            logToCon.log.info('file has already been archived.')
            return True
    logToCon.log.info('file has not been previously archived, beginning download and upload process...')
    return False
