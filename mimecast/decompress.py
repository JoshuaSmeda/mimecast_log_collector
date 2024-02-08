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
            partition = None
            for log_entry in c.get("data"):
                if log_entry.get("datetime"):
                    datetime = log_entry.get("datetime")
                    date = datetime.split("T")[0]
                    year = date.split("-")[0]
                    month = date.split("-")[1]
                    day = date.split("-")[2]
                    partition = f"{year}/{month}/{day}"
            if not partition:
                partition = "UNKNOWN"
            if not os.path.exists(f"{path}/{partition}"):
                os.makedirs(f"{path}/{partition}")
            with open(f"{path}/{partition}/{filename}", "wb") as o:
                log.debug(f"Writing {path}/{partition}/{filename}")
                o.write(str(c).encode('utf-8'))
    os.remove(zip_file_name)
    return f"{partition}"
