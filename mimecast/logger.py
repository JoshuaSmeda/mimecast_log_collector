import logging
import logging.handlers
import datetime
import os
from .Config import Config

Config = Config()

# Set up logging (in this case to terminal)
log = logging.getLogger(__name__)
log.root.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(levelname)s %(message)s')
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)


# Supporting methods
def get_hdr_date():
    date = datetime.datetime.utcnow()
    dt = date.strftime("%a, %d %b %Y %H:%M:%S")
    return dt + " UTC"


def get_current_date():
    date = datetime.datetime.now()
    # 2019-12-03T10:15:30+0000
    date = date.strftime("%Y-%m-%dT%H:%M:%S+0200")
    return date


def get_old_date(old_date=None):
    if old_date:
        old_datetime = datetime.datetime.strptime(old_date, "%Y-%m-%dT%H:%M:%S+0200")
        old_date_delta = datetime.datetime.now() - old_datetime
        date = datetime.datetime.now() - datetime.timedelta(seconds=old_date_delta.total_seconds())
    else:
        date = datetime.datetime.now() - datetime.timedelta(days=14)
    date = date.strftime("%Y-%m-%dT%H:%M:%S+0200")
    return date


def read_file(file_name):
    try:
        with open(file_name, 'r') as f:
            data = f.read()
        return data
    except Exception as e:
        log.error('Error reading file ' + file_name + '. Cannot continue. Exception: ' + str(e))
        quit()


def append_file(file_name, data_to_write):  # Do not append duplicate data to file
    try:
        found = False
        logfile = open(file_name, 'r')
        loglist = logfile.readlines()
        for line in loglist:
            if str(data_to_write) in line:
                found = True

        if not found:
            with open(file_name, 'a+', encoding="utf-8") as f:
                f.write(data_to_write + '\n')
    except Exception as e:
        log.error('Error reading file ' + file_name + '. Cannot continue. Exception: ' + str(e))
        quit()


def write_file(file_name, data_to_write):
    try:
        with open(file_name, 'w', encoding="utf-8") as f:
            f.write(data_to_write)
    except Exception as e:
        log.error('Error writing file ' + file_name + '. Cannot continue. Exception: ' + str(e))
        quit()


def delete_file(file_name):
    try:
        os.remove(file_name)
    except Exception as e:
        log.error('Error deleting file ' + file_name + '. Cannot continue. Exception: ' + str(e))
        quit()
