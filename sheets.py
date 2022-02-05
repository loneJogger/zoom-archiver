# imports
import os
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logToCon

# get user emails from google sheet
def getEmails():

    googs = {
        "type" : os.environ['GOOG_TYPE'],
        "project_id" : os.environ['GOOG_PROJECT_ID'],
        "private_key_id" : os.environ['GOOG_PRIVATE_KEY_ID'],
        "private_key" : os.environ['GOOG_PRIVATE_KEY'].replace('\\n', '\n'),
        "client_email" : os.environ['GOOG_CLIENT_EMAIL'],
        "client_id" : os.environ['GOOG_CLIENT_ID'],
        "auth_uri" : os.environ['GOOG_AUTH_URI'],
        "token_uri" : os.environ['GOOG_TOKEN_URI'],
        "auth_provider_x509_cert_url" : os.environ['GOOG_AUTH_PROVIDER_X509_CERT_URL'],
        "client_x509_cert_url" : os.environ['GOOG_CLIENT_X509_CERT_URL']
    }
    creds = service_account.Credentials.from_service_account_info(googs, scopes=["https://www.googleapis.com/auth/spreadsheets"], subject=os.environ['SUBJECT'])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    try:
        r1 = sheet.values().get(spreadsheetId=os.environ['SPREADSHEET_ID'], range=os.environ['RANGE_1']).execute()
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    res = set([])
    values = r1.get('values', [])
    if not values:
        logToCon.log.warn('no values found in range')
    else:
        for cell in values:
            if len(cell) > 0:
                res.add(cell[0].lower())
    return res
