from mimecast.connection import Mimecast
import os
import time
from mimecast.logger import log, syslogger, write_file, read_file
from mimecast.decompress import unpack_and_write
from mimecast.s3 import copy_to_s3
import mimecast.Config

# Configuration details
Config = mimecast.Config.Config()

# Declare the type of event we want to ingest
event_type = '/api/audit/get-siem-logs'
event_category = 'siem'
connection = Mimecast(event_type)
interval_time = Config.get_logging_details()['INTERVAL_TIMER']


def init_directory(event_category):
    if not os.path.exists(Config.get_logging_details()['LOG_FILE_PATH'] + str(event_category)):
        os.makedirs(Config.get_logging_details()['LOG_FILE_PATH'] + str(event_category))


def get_mta_siem_logs(checkpoint_dir, base_url, access_key, secret_key):
    # Set checkpoint file name to store page token
    checkpoint_filename = os.path.join(checkpoint_dir, 'get_mta_siem_logs_checkpoint')

    # Build post body for request
    post_body = dict()
    post_body['data'] = [{}]
    post_body['data'][0]['type'] = 'MTA'
    post_body['data'][0]['fileFormat'] = 'JSON'
    if Config.get_api_options()['COMPRESSED'] is True:
        post_body['data'][0]['compress'] = 'true'
    if os.path.exists(checkpoint_filename):
        post_body['data'][0]['token'] = read_file(checkpoint_filename)

    # Send request to API
    resp = connection.post_request(base_url, event_type, post_body, access_key, secret_key)

    # Process response
    if resp != 'error':
        resp_body = resp[0]
        resp_headers = resp[1]
        resp_status = resp[2]
        content_type = resp_headers['Content-Type']

        if resp_status == 429:
            log.warn('Rate limit hit. Sleeping for %s' % str(resp_headers['X-RateLimitReset']))
            rate_limit = (int(resp_headers['X-RateLimit-Reset']) / 1000 % 60)
            time.sleep(rate_limit * 20)

        # End if response is JSON as there is no log file to download
        if content_type == 'application/json':
            log.info('No more SIEM logs available - Resting for 60 seconds')
            time.sleep(60)
            return True

        # Process log file
        elif content_type == 'application/octet-stream':
            try:
                # Save file to log file path
                filename_list = []
                if Config.get_api_options()['COMPRESSED'] is True:
                    log.debug("Unpacking compressed data")
                    log_dir = unpack_and_write(resp_body, Config.get_logging_details()['LOG_FILE_PATH'])
                    for file_name in os.listdir(f"{Config.get_logging_details()['LOG_FILE_PATH']}/{log_dir}"):
                        filename_list.append(file_name)
                else:
                    log.debug("Processing uncompressed data")
                    file_name = resp_headers['Content-Disposition'].split('=\"')
                    file_name = file_name[1][:-1]
                    write_file(os.path.join(Config.get_logging_details()['LOG_FILE_PATH'], file_name), resp_body)
                    filename_list.append(file_name)
            except Exception as e:
                print(e)

            try:
                for log_file in filename_list:
                    try:
                        if Config.get_syslog_details()['syslog_output'] is True:
                            log.info('Loading file: ' + os.path.join(Config.get_logging_details()['LOG_FILE_PATH'], file_name) + ' to output to ' + Config.get_syslog_details()['syslog_server'] + ':' + str(Config.get_syslog_details()['syslog_port']))
                            with open(os.path.join(Config.get_logging_details()['LOG_FILE_PATH'], file_name), 'r') as log_file:
                                lines = log_file.read().splitlines()
                                for line in lines:
                                    syslogger.info(line)
                            log.info('Syslog output completed for file ' + file_name)
                        if Config.get_s3_options()['COPY_TO_S3'] is True:
                            copy_to_s3(log_dir, log_file, Config.get_logging_details()['LOG_FILE_PATH'], Config.get_s3_options()['S3_BUCKET'])
                    except Exception as e:
                        log.error('Unexpected error writing to syslog. Exception: ' + str(e))

                # Save mc-siem-token page token to check point directory
                write_file(checkpoint_filename, resp_headers['mc-siem-token'])
                # return true to continue loop
                return True

            except Exception as e:
                log.error("Error writing log files")
                log.error(e)
                return True  # continue loop

        else:
            # Handle errors
            log.error('Unexpected response')
            for header in resp_headers:
                log.error(header)
            return False


def get_siem_logs():
    try:
        base_url = connection.get_base_url(Config.get_email_address())
        print(base_url)
    except Exception:
        log.error('Error discovering base url for %s. Please double check mimecast/Config.py' % (Config.get_email_address()))
        quit()

    # Request log data in a loop until there are no more logs to collect
    try:
        log.info('Getting MTA log data')
        while get_mta_siem_logs(checkpoint_dir=Config.get_logging_details()['CHK_POINT_DIR'], base_url=base_url, access_key=Config.get_access_key(), secret_key=Config.get_secret_key()) is True:
            log.info("Getting additional SIEM logs")
    except Exception as e:
        log.error('Unexpected error getting MTA logs ' + (str(e)))
    quit()


get_siem_logs()
