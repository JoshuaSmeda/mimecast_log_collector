import configuration
from mimecast.connection import Mimecast
import os
import time
import requests
from mimecast.logger import log, syslogger, write_file, read_file

# Declare the type of event we want to ingest
event_type = '/api/audit/get-audit-events'
connection = Mimecast(event_type)


def get_audit_siem_logs(base_url, access_key, secret_key):
    post_body = dict()
    post_body['data'] = [{'startDateTime': '2018-12-03T10:15:30+0000','endDateTime': '2019-12-03T10:15:30+0000'}]
    print(post_body)
    resp = connection.post_request(base_url, event_type, post_body, access_key, secret_key)
    print(resp)

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
    
        else:
            # Handle errors
            log.error('Unexpected response')
            for header in resp_headers:
                log.error(header)
            return False

    else:
        print("ERROR!")


def get_audit_logs(): 
    try:
        base_url = connection.get_base_url(configuration.authenication_details['EMAIL_ADDRESS'])
        print(base_url)
    except Exception:
        log.error('Error discovering base url for %s. Please double check configuration.py' % (configuration.authenication_details['EMAIL_ADDRESS']))
        quit()

    # Request log data in a loop until there are no more logs to collect
    try:
        log.info('Getting Audit log data')
        while get_audit_siem_logs(base_url=base_url, access_key=configuration.authenication_details['ACCESS_KEY'], secret_key=configuration.authenication_details['SECRET_KEY']) is True:
            print("Getting additional SIEM logs")
    except Exception as e:
        log.error('Unexpected error getting MTA logs ' + (str(e)))
    quit()

# Start ingesting logs!
get_audit_logs()
