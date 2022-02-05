import os
import sheets
import dynamo
import zoom
import bucket
import report

USERS_TABLE = os.environ['USERS_TABLE']
FILES_TABLE = os.environ['FILES_TABLE']
AGE = os.environ['AGE']
BUCKET = os.environ['BUCKET']
reportUsers = []
reportFiles = []

userEmails = sheets.getEmails()
usersFromTable = dynamo.getAll(USERS_TABLE)
changes = dynamo.compareSheetToTable(userEmails, usersFromTable)
dynamo.writeChanges(USERS_TABLE, changes)
activeUsers = dynamo.getActive(USERS_TABLE)
date_ranges = zoom.buildRanges()
for user in activeUsers:
    all_meetings = zoom.getMeetings(user)
    old_meetings = zoom.checkForOld(all_meetings, int(AGE))
    if len(old_meetings) >= 1:
        files = zoom.getUrls(old_meetings)
        reportUsers.append(user['email']['S'])
        filesArr = []
        for file in files:
            if not dynamo.checkForFile(FILES_TABLE, file):
                file_name = zoom.download(file)
                filesArr.append(file_name)
                isUploaded = bucket.upload(file_name, BUCKET, user)
                if isUploaded:
                    dynamo.writeCompletedFile(FILES_TABLE, file, file_name, user)
                if file_name:
                    zoom.delete(file_name)
        reportFiles.append(filesArr)
    else:
        print('this user has no meetings to archive')
report.createReport(reportUsers, reportFiles)
report.sendMail(reportUsers, reportFiles)
print('process finished!')
