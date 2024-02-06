from mimecast.connection import Mimecast
import os
import time
import json
import hashlib
import mimecast.Config
from mimecast.logger import log, syslogger

# Configuration details
Config = mimecast.Config.Config()

# Declare the type of event we want to ingest
event_type = '/api/ttp/url/get-logs'
event_category = 'ttp/'
connection = Mimecast(event_type)
interval_time = Config.get_logging_details()['INTERVAL_TIMER']


def init_directory(event_category):
    if not os.path.exists(Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category)):
        os.makedirs(Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category))
    else:
        print("dir exist")


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
            log.info('No more TTP URL logs available - Resting temporarily')
            time.sleep(interval_time)
            return True

        # Process log file
        elif 'application/json' in content_type:
            file_name = 'ttp_events'  # Storing everything into one file
            rjson = json.loads(resp_body)
            resp_body = rjson['data'][0]['clickLogs']  # Get TTP urls

            # Forward each event individually
            for row in resp_body:
                row = str(row).replace("'", '"')  # Convert audit event to valid JSON

                try:
                    if Config.get_syslog_details()['syslog_output'] is True:
                        hashed_event = (hashlib.md5(row.encode('utf-8')).hexdigest())
                        if os.path.isfile(Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category) + str(hashed_event)):  # If true
                            print("Hash already exists in %s" % Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category) + str(hashed_event))
                        else:
                            log.info("Creating hash %s in %s and forwarding to configured syslog" % (hashed_event, Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category)))
                            os.mknod(Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category) + str(hashed_event))
                            syslogger.info(row)

                        log.info("Syslog output completed for %s" % str(event_category))

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


def get_ttp_logs():
    try:
        base_url = connection.get_base_url(Config.get_email_address())
        print(base_url)
    except Exception:
        log.error('Error discovering base url for %s. Please double check mimecast/Config.py' % (Config.get_email_address()))
        quit()

    # Request log data in a loop until there are no more logs to collect
    try:
        log.info('Getting TTP log data')
        while Get_TTPURL_events(base_url=base_url, access_key=Config.get_access_key(), secret_key=Config.get_secret_key()) is True:
            print("Getting additional TTP logs after %s seconds" % (interval_time))
            time.sleep(interval_time)
    except Exception as e:
        log.error('Unexpected error getting TTP logs ' + (str(e)))
    quit()


init_directory(event_category)
get_ttp_logs()
