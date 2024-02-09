import os
import time
import json
# import hashlib
import mimecast.Config
from mimecast.connection import Mimecast
from mimecast.s3 import copy_to_s3
from mimecast.paramstore import get_ssm_parameter, put_ssm_paramter
from mimecast.logger import log, get_current_date, get_old_date
import random
import string


# Configuration details
Config = mimecast.Config.Config()

# Declare the type of event we want to ingest
event_type = '/api/audit/get-audit-events'
event_category = 'audit/'
connection = Mimecast(event_type)
interval_time = Config.get_logging_details()['INTERVAL_TIMER']


def init_directory(event_category):
    if not os.path.exists(Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category)):
        os.makedirs(Config.get_logging_details()['CHK_POINT_DIR'] + str(event_category))


def get_audit_events(base_url, access_key, secret_key):
    post_body = dict()
    current_date = get_current_date()
    audit_checkpoint = get_ssm_parameter(Config.get_logging_details()['CHK_POINT_CLOUD_LOCATION_AUDIT'])
    if Config.get_logging_details()["CHK_POINT_CLOUD"] and audit_checkpoint != "INITVALUE":
        post_body['data'] = [{'startDateTime': get_old_date(old_date=audit_checkpoint), 'endDateTime': current_date}]
    else:
        post_body['data'] = [{'startDateTime': get_old_date(), 'endDateTime': current_date}]
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
            file_name = f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))}.json"  # Storing everything into one file
            rjson = json.loads(resp_body)
            resp_body = rjson['data']  # Get Audit urls

            # Forward each event individually
            for row in resp_body:
                row = str(row).replace("'", '"')  # Convert audit event to valid JSON

                try:
                    current_date_pre = current_date.split("T")[0]
                    log_dir = f'audit_events/{current_date_pre.split("-")[0]}/{current_date_pre.split("-")[1]}/{current_date_pre.split("-")[2]}'
                    if not os.path.exists(f"{Config.get_logging_details()['LOG_FILE_PATH']}/{file_name}/{log_dir}"):
                        os.makedirs(f"{Config.get_logging_details()['LOG_FILE_PATH']}/{file_name}/{log_dir}")
                    with open(f"{Config.get_logging_details()['LOG_FILE_PATH']}/{file_name}/{log_dir}/{file_name}", "w") as o:
                        o.write(json.dumps(resp_body))

                    if Config.get_s3_options()['COPY_TO_S3'] is True:
                        copy_to_s3(log_dir, file_name, f"{Config.get_logging_details()['LOG_FILE_PATH']}/{file_name}", Config.get_s3_options()['S3_BUCKET'])

                except Exception as e:
                    log.error('Unexpected error writing to log data. Exception: ' + str(e))

            put_ssm_paramter(Config.get_logging_details()['CHK_POINT_CLOUD_LOCATION_AUDIT'], current_date)
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
        base_url = connection.get_base_url(Config.get_email_address())
    except Exception:
        log.error('Error discovering base url for %s. Please double check configuration.py' % (Config.get_email_address()))
        quit()

    try:
        log.info('Getting Audit log data')
        while get_audit_events(base_url=base_url, access_key=Config.get_access_key(), secret_key=Config.get_secret_key()) is True:
            log.info("Getting additional Audit logs after %s seconds" % (interval_time))
            time.sleep(interval_time)
    except Exception as e:
        log.error('Unexpected error getting Audit logs ' + (str(e)))
    quit()


init_directory(event_category)
get_audit_logs()
