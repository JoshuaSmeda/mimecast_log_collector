import configuration
from mimecast.connection import Mimecast
import os
import time
import requests
import json
import hashlib
from mimecast.logger import log, syslogger, write_file, read_file, append_file


# Declare the type of event we want to ingest
event_type = '/api/ttp/url/get-logs'
connection = Mimecast(event_type)


def Get_TTPURL_events(base_url, access_key, secret_key):
    post_body = dict()
    resp = connection.post_request(base_url, event_type, post_body, access_key, secret_key)

    # Process response
    if resp != 'error':
        resp_body = resp[0]
        resp_headers = resp[1]
        content_type = resp_headers['Content-Type']

        # No more TTP events available
        if 'application/json' not in content_type:
            log.info('No more TTP URL logs available - Resting for 60 seconds')
            time.sleep(60)
            return True

        # Process log file
        elif 'application/json' in content_type:
            file_name = 'ttp_events' # Storing everything into one file
            rjson = json.loads(resp_body)
            resp_body = rjson['data'][0]['clickLogs'] # Get TTP urls

            # Forward each event individually
            for row in resp_body:
                row = str(row).replace("'", '"') # Convert audit event to valid JSON

                # Save file to log file path
                append_file(os.path.join(configuration.logging_details['LOG_FILE_PATH'], file_name), str(row))

                try:
                    if configuration.syslog_details['syslog_output'] is True:
                        log.info('Loading file: ' + os.path.join(configuration.logging_details['LOG_FILE_PATH'], file_name) + ' to output to ' + configuration.syslog_details['syslog_server'] + ':' + str(configuration.syslog_details['syslog_port']))
                        with open(os.path.join(configuration.logging_details['LOG_FILE_PATH'], file_name), 'r') as log_file:
                            lines = log_file.read().splitlines()
                            for line in lines:
                                hashed_event = (hashlib.md5(line.encode('utf-8')).hexdigest())
                                with open('hash_file', 'r') as hash_file:
                                    if (hashed_event + '\n') in hash_file.readlines():
                                        print("Hash %s already exists" % (hashed_event))
                                    else:
                                        syslogger.info(line)
                                        append_file('hash_file', hashed_event)

                        log.info('Syslog output completed for file ' + file_name)

                except Exception as e:
                    log.error('Unexpected error writing to syslog. Exception: ' + str(e))

            # Return True to continue loop
            time.sleep(5)
            return True

        else:
            # Handle errors
            log.error('Unexpected response')
            for header in resp_headers:
                log.error(header)
            return False


def get_ttp_logs():
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
