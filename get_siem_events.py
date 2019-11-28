import configuration
from mimecast.connection import Mimecast
import os
import time
from mimecast.logger import log, syslogger, write_file, read_file


# Declare the type of event we want to ingest
event_type = '/api/audit/get-siem-logs'
connection = Mimecast(event_type)


def get_mta_siem_logs(checkpoint_dir, base_url, access_key, secret_key):
    # Set checkpoint file name to store page token
    checkpoint_filename = os.path.join(checkpoint_dir, 'get_mta_siem_logs_checkpoint')

    # Build post body for request
    post_body = dict()
    post_body['data'] = [{}]
    post_body['data'][0]['type'] = 'MTA'
    if os.path.exists(checkpoint_filename):
        post_body['data'][0]['token'] = read_file(checkpoint_filename)

    # Send request to API
    resp = connection.post_request(base_url, event_type, post_body, access_key, secret_key)

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

            # Save file to log file path
            write_file(os.path.join(configuration.logging_details['LOG_FILE_PATH'], file_name), resp_body)
            # Save mc-siem-token page token to check point directory
            write_file(checkpoint_filename, resp_headers['mc-siem-token'])
            try:
                if configuration.syslog_details['syslog_output'] is True:
                    log.info('Loading file: ' + os.path.join(configuration.logging_details['LOG_FILE_PATH'], file_name) + ' to output to ' + configuration.syslog_details['syslog_server'] + ':' + str(configuration.syslog_details['syslog_port']))
                    with open(os.path.join(configuration.logging_details['LOG_FILE_PATH'], file_name), 'r') as log_file:
                        lines = log_file.read().splitlines()
                        for line in lines:
                            syslogger.info(line)
                    log.info('Syslog output completed for file ' + file_name)
            except Exception as e:
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
        base_url = connection.get_base_url(configuration.authenication_details['EMAIL_ADDRESS'])
        print(base_url)
    except Exception:
        log.error('Error discovering base url for %s. Please double check configuration.py' % (configuration.authenication_details['EMAIL_ADDRESS']))
        quit()

    # Request log data in a loop until there are no more logs to collect
    try:
        log.info('Getting MTA log data')
        while get_mta_siem_logs(checkpoint_dir=configuration.logging_details['CHK_POINT_DIR'], base_url=base_url, access_key=configuration.authenication_details['ACCESS_KEY'], secret_key=configuration.authenication_details['SECRET_KEY']) is True:
            print("Getting additional SIEM logs")
    except Exception as e:
        log.error('Unexpected error getting MTA logs ' + (str(e)))
    quit()

# Start ingesting logs!


get_siem_logs()