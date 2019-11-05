import json
import os
import requests
import base64
import uuid
import datetime
import hashlib
import hmac
import time
import threading
# Import logging functions
from mimecast import logger

LOG_FILE_PATH = "FULLY QUALIFIED PATH TO FOLDER TO WRITE LOGS"
CHK_POINT_DIR = 'FULLY QUALIFIED PATH TO FOLDER TO WRITE PAGE TOKEN'
 
syslog_output = True
syslog_server = '127.0.0.1'
syslog_port = 5114

def create_signature(data_to_sign, secret_key):
    digest = hmac.new(secret_key.decode("base64"), data_to_sign, digestmod=hashlib.sha1).digest()
    return base64.encodestring(digest).rstrip()


def get_base_url(email_address):
    # Create post body for request
    post_body = dict()
    post_body['data'] = [{}]
    post_body['data'][0]['emailAddress'] = email_address

    # Create variables required for request headers
    request_id = str(uuid.uuid4())
    request_date = get_hdr_date()
    headers = {'x-mc-app-id': APP_ID, 'x-mc-req-id': request_id, 'x-mc-date': request_date}

    # Send request to API
    log.debug('Sending request to https://api.mimecast.com/api/discover-authentication with request Id: ' +
                  request_id)
    try:
        r = requests.post(url='https://api.mimecast.com/api/login/discover-authentication',
                          data=json.dumps(post_body), headers=headers)
        # Handle Rate Limiting
        if r.status_code == 429:
            rate_limit = (int(r.headers['X-RateLimit-Reset'])/1000) % 60
            time.sleep(rate_limit * 20)
    except Exception, e:
        log.error('Unexpected error getting base url. Cannot continue.' + str(e))
        quit()

    # Handle error from API
    if r.status_code != 200:
        log.error('Request returned with status code: ' + str(r.status_code) + ', response body: ' + r.text + '. Cannot continue.')
        quit()

    # Load response body as JSON
    resp_data = json.loads(r.text)

    # Look for api key in region region object to get base url
    if 'region' in resp_data["data"][0]:
        base_url = resp_data["data"][0]["region"]["api"].split('//')
        base_url = base_url[1]
    else:
        # Handle no region found, likely the email address was entered incorrectly
        log.error('No region information returned from API, please check the email address. Cannot continue')
        quit()

    return base_url


def post_request(base_url, uri, post_body, access_key, secret_key):
    # Create variables required for request headers
    request_id = str(uuid.uuid4())
    request_date = get_hdr_date()
    signature = 'MC ' + access_key + ':' + create_signature(':'.join(
        [request_date, request_id, uri, APP_KEY]), secret_key)

    headers = {'Authorization': signature, 'x-mc-app-id': APP_ID, 'x-mc-req-id': request_id, 'x-mc-date': request_date}

    try:
        # Send request to API
        log.debug('Sending request to https://' + base_url + uri + ' with request Id: ' + request_id)
        r = requests.post(url='https://' + base_url + uri, data=json.dumps(post_body), headers=headers)

        # Handle Rate Limiting
        if r.status_code == 429:
            log.warn('Rate limit hit. Sleeping for ' + str(r.headers['X-RateLimit-Reset']))
            rate_limit = (int(r.headers['X-RateLimit-Reset'])/1000)%60
            time.sleep(rate_limit * 20)

    # Handle errors on client side
    except Exception, e:
        log.error('Unexpected error connecting to API. Exception: ' + str(e))
        return 'error'

    # Handle errors from API
    if r.status_code != 200:
        log.error('Request to ' + uri + ' with , request id: ' + request_id + ' returned with status code: ' + str(r.status_code) + ', response body: ' + r.text)
        run_script()

    # Return response body and response headers
    return r.text, r.headers


def get_mta_siem_logs(checkpoint_dir, base_url, access_key, secret_key):
    uri = "/api/audit/get-siem-logs"

    # Set checkpoint file name to store page token
    checkpoint_filename = os.path.join(checkpoint_dir, 'get_mta_siem_logs_checkpoint')

    # Build post body for request
    post_body = dict()
    post_body['data'] = [{}]
    post_body['data'][0]['type'] = 'MTA'
    if os.path.exists(checkpoint_filename):
        post_body['data'][0]['token'] = read_file(checkpoint_filename)

    # Send request to API
    resp = post_request(base_url, uri, post_body, access_key, secret_key)

    # Process response
    if resp != 'error':
        resp_body = resp[0]
        resp_headers = resp[1]
        content_type = resp_headers['Content-Type']

        # End if response is JSON as there is no log file to download
        if content_type == 'application/json':
            log.info('No more SIEM logs available - Resting for 60 seconds')
            time.sleep(60)
            return True

        # Process log file
        elif content_type == 'application/octet-stream':
            file_name = resp_headers['Content-Disposition'].split('=\"')
            file_name = file_name[1][:-1]

            # Save file to LOG_FILE_PATH
            write_file(os.path.join(LOG_FILE_PATH, file_name), resp_body)
            # Save mc-siem-token page token to check point directory
            write_file(checkpoint_filename, resp_headers['mc-siem-token'])
            try:
                if syslog_output is True:
                    log.info('Loading file: ' + os.path.join(LOG_FILE_PATH, file_name) + ' to output to ' +
                                                             syslog_server + ':' + str(syslog_port))
                    with open(os.path.join(LOG_FILE_PATH, file_name), 'r') as log_file:
                        lines = log_file.read().splitlines()
                        for line in lines:
                            syslogger.info(line)
                    log.info('Syslog output completed for file ' + file_name)
            except Exception, e:
                log.error('Unexpected error writing to syslog. Exception: ' + str(e))

            # return true to continue loop
            return True
        else:
            # Handle errors
            log.error('Unexpected response')
            for header in resp_headers:
                log.error(header)
            return False


def get_siem_logs():
    try:
        base_url = get_base_url(email_address=EMAIL_ADDRESS)
    except Exception, e:
        log.error('Error discovering base url for ' + EMAIL_ADDRESS + ' . Exception: ' + str(e))
        quit()

    # Request log data in a loop until there are no more logs to collect
    try:
        log.info('Getting MTA log data')
        while get_mta_siem_logs(checkpoint_dir=CHK_POINT_DIR, base_url=base_url, access_key=ACCESS_KEY, secret_key=SECRET_KEY) is True:
            log.info('Requesting more SIEM log files')
    except Exception, e:
        log.error('Unexpected error getting MTA logs ' + (str(e)))
    quit()

def get_audit_logs():
    log.info("Getting audit logs here")


# Init threading example here:
#    get_siem_logs()