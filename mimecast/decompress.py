import os
import zipfile
import random
import string
import json
from .logger import log


def unpack_and_write(resp_body: bytes, path: string):
    """Unpack the zip file and gzip each
    json file contained within. Place in a directory
    based on date
    """
    zip_file_name = f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))}.zip"

    o = open(zip_file_name, "wb")
    o.write(resp_body)
    o.close()

    zip_file = zipfile.ZipFile(zip_file_name)
    for filename in zip_file.namelist():
        with zip_file.open(filename, mode="r") as f:
            c = json.loads(f.read())
            filename_base = filename.split('.')[0]
            event_day = filename_base.split('_')[-1]
            year = event_day[0:4]
            month = event_day[4:6]
            day = event_day[6:]
            if not os.path.exists(f"{path}/{year}"):
                os.mkdir(f"{path}/{year}")
            if not os.path.exists(f"{path}/{year}/{month}"):
                os.mkdir(f"{path}/{year}/{month}")
            if not os.path.exists(f"{path}/{year}/{month}/{day}"):
                os.mkdir(f"{path}/{year}/{month}/{day}")
            with open(f"{path}/{year}/{month}/{day}/{filename}", "wb") as o:
                log.debug(f"Writing {path}/{year}/{month}/{day}/{filename}")
                o.write(str(c).encode('utf-8'))
    os.remove(zip_file_name)
    return f"{year}/{month}/{day}"
