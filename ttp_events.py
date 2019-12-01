import configuration
from mimecast.connection import Mimecast
import os
import time
import requests
from mimecast.logger import log, syslogger, write_file, read_file

# Declare the type of event we want to ingest
event_type = '/api/ttp/url/get-logs'
connection = Mimecast(event_type)


def Get_TTPURL_events(base_url, access_key, secret_key):
    post_body = dict()
   # post_body['data'] = [{'startDateTime': '2018-12-03T10:15:30+0000','endDateTime': '2019-12-03T10:15:30+0000'}]
    resp = connection.post_request(base_url, event_type, post_body, access_key, secret_key)

    # Process response
    if resp != 'error':
        resp_body = resp[0]
        resp_headers = resp[1]
        content_type = resp_headers['Content-Type']

        # End if response is JSON as there is no log file to download
        if content_type == 'application/json':
            log.info('No more TTP URL logs available - Resting for 60 seconds')
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


def get_ttp_logss(): 
    try:
        base_url = connection.get_base_url(configuration.authenication_details['EMAIL_ADDRESS'])
        print(base_url)
    except Exception:
        log.error('Error discovering base url for %s. Please double check configuration.py' % (configuration.authenication_details['EMAIL_ADDRESS']))
        quit()

    # Request log data in a loop until there are no more logs to collect
    try:
        log.info('Getting TTP log data')
        while Get_TTPURL_events(base_url=base_url, access_key=configuration.authenication_details['ACCESS_KEY'], secret_key=configuration.authenication_details['SECRET_KEY']) is True:
            print("Getting additional TTP logs")
    except Exception as e:
        log.error('Unexpected error getting TTP logs ' + (str(e)))
    quit()

get_ttp_logs()