# imports
import os
import json
import jwt
import http.client
import requests
from datetime import date, timedelta, datetime
import logToCon

ZOOM_API_KEY = os.environ['ZOOM_API_KEY']
ZOOM_API_SECRET = os.environ['ZOOM_API_SECRET']

# form date ranges to query api with
def buildRanges():

    ranges = []
    begin = date.today()
    for x in range(0,5):
        end = begin - timedelta(days=29)
        ranges.append({ "from" : end.strftime("%Y-%m-%d"), "to" : begin.strftime("%Y-%m-%d") })
        begin = begin - timedelta(days=30)
    return ranges

# build jwt for call
def buildJWT():

    payload = {
    'iss' : ZOOM_API_KEY,
    'exp' : datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, ZOOM_API_SECRET)
    return token

# get all meetings of a user from now to 150 days ago
def getMeetings(user):

    meetings = []
    ranges = buildRanges()
    token = buildJWT()
    headers = {
        "authorization": "Bearer {}".format(token),
        "content-type": "application/json"
        }
    for time in ranges:
        begin = time['from']
        end = time['to']
        conn = http.client.HTTPSConnection('api.zoom.us')
        req = "/v2/users/{}/recordings?page_size=30&to={}&from={}".format(user['email']['S'], end, begin)
        try:
            conn.request("GET", req, headers=headers)
            res = conn.getresponse()
        except RuntimeError as e:
            logToCon.log.error(e)
            return False
        data = res.read()
        dataJson = json.loads(data)
        if 'meetings' in dataJson:
            meetings.extend(dataJson['meetings'])
            while len(dataJson['next_page_token']) > 0:
                nextPage = dataJson['next_page_token']
                conn = http.client.HTTPSConnection('api.zoom.us')
                req = "/v2/users/{}/recordings?page_size=30&to={}&from={}&next_page_token={}".format(user['email']['S'], end, begin, nextPage)
                try:
                    conn.request("GET", req, headers=headers)
                    res = conn.getresponse()
                except RuntimeError as e:
                    logToCon.log.error(e)
                    return False
                data = res.read()
                dataJson = json.loads(data)
                if 'meetings' in dataJson:
                    meetings.extend(dataJson['meetings'])
    logToCon.log.info('found {} meetings for {} in the last 150 days.'.format(len(meetings), user))
    return meetings

# limit meetings based on if they are old enough to require downloading
def checkForOld(meetings, age):

    old = []
    for meeting in meetings:
        start = datetime.strptime(meeting['start_time'], "%Y-%m-%dT%H:%M:%SZ")
        old_enough = datetime.utcnow() - timedelta(days=age)
        if start < old_enough:
            old.append(meeting)
    return old

# get urls for files to download
def getUrls(meetings):

    urls = []
    for meeting in meetings:
        for recording in meeting['recording_files']:
            if recording['status'] != 'processing':
                urls.append({
                    "url" : recording['download_url'],
                    "type" : recording['file_extension'],
                    "time" : recording['recording_start'],
                    "desc" : recording['recording_type'],
                    "recording_id": recording['id']
                })
    return urls

# download just one file
def download(file):

    full_url = "{}?access_token={}".format(file['url'], buildJWT())
    try:
        r = requests.get(full_url, stream=True)
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    file_name = "{}{}.{}".format(file['time'].replace(':', '-'), file['desc'], file['type']).lower()
    with open(file_name, "wb") as f:
        for chunk in r.iter_content(chunk_size=(32*1024)):
            if chunk:
                f.write(chunk)
    logToCon.log.info('{} downloaded from zoom.'.format(file_name))
    return file_name

# delete local copy of file
def delete(file):

    encrypted = 'enc_' + file
    try:
        os.remove(file)
        # os.remove(encrypted)
    except RuntimeError as e:
        logToCon.log.error(e)
        return False
    logToCon.log.info('{} successfully deleted.'.format(file))
