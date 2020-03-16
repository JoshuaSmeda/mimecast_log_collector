import configuration
import os
import time
import requests
import json
import hashlib

from mimecast.connection import Mimecast
from mimecast.logger import log, syslogger, write_file, read_file, append_file, get_hdr_date, get_current_date, get_old_date

# Declare the type of event we want to ingest
event_type = '/api/audit/get-audit-events'
event_category = 'audit/'
connection = Mimecast(event_type)
interval_time = configuration.logging_details['INTERVAL_TIMER']


def init_directory(event_category):
  if not os.path.exists(configuration.logging_details['CHK_POINT_DIR'] + str(event_category)):
    os.makedirs(configuration.logging_details['CHK_POINT_DIR'] + str(event_category))


def get_audit_events(base_url, access_key, secret_key):
    post_body = dict()
    post_body['data'] = [{ 'startDateTime': get_old_date(), 'endDateTime': get_current_date() }]
    resp = connection.post_request(base_url, event_type, post_body, access_key, secret_key)

    # Process response
    if resp != 'error':
        resp_body = resp[0]
        resp_headers = resp[1]
        content_type = resp_headers['Content-Type']

        # No more TTP events available
        if 'application/json' not in content_type:
            log.info('No additional Audit logs available - Resting temporarily')
            time.sleep(interval_time)
            return True

        # Process log file
        elif 'application/json' in content_type:
            file_name = 'audit_events' # Storing everything into one file
            rjson = json.loads(resp_body)
            resp_body = rjson['data'] # Get Audit urls

            # Forward each event individually
            for row in resp_body:
                row = str(row).replace("'", '"') # Convert audit event to valid JSON

                try:
                    if configuration.syslog_details['syslog_output'] is True:
                        hashed_event = (hashlib.md5(row.encode('utf-8')).hexdigest())
                        if os.path.isfile(configuration.logging_details['CHK_POINT_DIR'] + str(event_category) + str(hashed_event)): # If true
                          print("Hash already exists in %s" % configuration.logging_details['CHK_POINT_DIR'] + str(event_category) + str(hashed_event))
                        else:
                          log.info("Creating hash %s in %s and forwarding to configured syslog" % (hashed_event, configuration.logging_details['CHK_POINT_DIR'] + str(event_category)))
                          os.mknod(configuration.logging_details['CHK_POINT_DIR'] + str(event_category) + str(hashed_event))
                          syslogger.info(row)

                        log.info("Syslog output completed for %s" % (event_category))

                except Exception as e:
                    log.error('Unexpected error writing to syslog. Exception: ' + str(e))

            # Return True to continue loop
            return True

        else:
            # Handle errors
            log.error('Unexpected response')
            for header in resp_headers:
                log.error(header)
            return False

def get_audit_logs():
    try:
        base_url = connection.get_base_url(configuration.authenication_details['EMAIL_ADDRESS'])
    except Exception:
        log.error('Error discovering base url for %s. Please double check configuration.py' % (configuration.authenication_details['EMAIL_ADDRESS']))
        quit()

    try:
        log.info('Getting Audit log data')
        while get_audit_events(base_url=base_url, access_key=configuration.authenication_details['ACCESS_KEY'], secret_key=configuration.authenication_details['SECRET_KEY']) is True:
            log.info("Getting additional Audit logs after %s seconds" % (interval_time))
            time.sleep(interval_time)
    except Exception as e:
        log.error('Unexpected error getting Audit logs ' + (str(e)))
    quit()

init_directory(event_category)
get_audit_logs()
