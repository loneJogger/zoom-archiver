import os
import mailchimp_transactional as MailChimp
from mailchimp_transactional.api_client import ApiClientError
from datetime import datetime

CLIENT_ID = os.environ['MAILCHIMP_CLIENT_ID']
FROM = os.environ['FROM_EMAIL']
TO = os.environ['TO_EMAIL']

def createReport(users, files):
    counter = 0
    print('USERS:')
    for user in users:
        print('{} had {} files:'.format(user, len(files[counter])))
        for file in files[counter]:
            print(file)
        counter += 1

def sendMail(users, files):

    time = str(datetime.utcnow())
    body = ""

    count = 0
    for user in users:
        body += "\n{}:\n".format(user)
        for file in files[count]:
            body += " - {}\n".format(file)
        count += 1

    if len(users) is 0:
        body = "No files to archive at this time."

    try:
        mailer = MailChimp.Client(CLIENT_ID)
        message = {
            "from_email": FROM,
            "subject": "Zoom Archiver Report",
            "text": "Time run: {}\n".format(time) + body,
            "to": [
                {
                    "email": TO,
                    "type": "to"
                }
            ]
        }
        response = mailer.messages.send({"message": message})
    except ApiClientError as error:
        print('error: {}'.format(error.text))
