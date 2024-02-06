import boto3


class Config():

    def __init__(self):
        self.source_details = {
            "siem_events": True,
            "ttp_events": True,
            "audit_events": True
        }
        self.syslog_details = {
            'syslog_output': False,
            'syslog_server': '127.0.0.1',
            'syslog_port': 5114,
        }

        self.logging_details = {
            'LOG_FILE_PATH': 'logs/',
            'CHK_POINT_DIR': 'hashes/',
            'INTERVAL_TIMER': 60
        }

        self.api_options = {
            'COMPRESSED': True
        }

        self.s3_options = {
            'COPY_TO_S3': True,
            'S3_BUCKET': ""
        }
        self.authentication_details = {
            'PARAMETER_STORE':  True,
            'PARAMETER_STORE_APP_ID': '/mimecast_logs/api_id',
            'PARAMETER_STORE_APP_KEY': '/mimecast_logs/app_key',
            'PARAMETER_STORE_ACCESS_KEY': '/mimecast_logs/access_key',
            'PARAMETER_STORE_SECRET_KEY': '/mimecast_logs/secret_key',
            'PARAMETER_STORE_EMAIL_ADDRESS': '/mimecast_logs/email_address',
            'APP_ID': "",
            'APP_KEY': "",
            'EMAIL_ADDRESS': '',
            'ACCESS_KEY': '',
            'SECRET_KEY': '',
        }

        if self.authentication_details["PARAMETER_STORE"] is True:
            ps = boto3.client("ssm")
            try:
                resp = ps.get_parameter(
                    Name=self.authentication_details["PARAMETER_STORE_APP_ID"],
                    WithDecryption=True
                )
                self.mimecast_app_id = resp.get("Parameter").get("Value")

                resp = ps.get_parameter(
                    Name=self.authentication_details["PARAMETER_STORE_APP_KEY"],
                    WithDecryption=True
                )
                self.mimecast_app_key = resp.get("Parameter").get("Value")

                resp = ps.get_parameter(
                    Name=self.authentication_details["PARAMETER_STORE_ACCESS_KEY"],
                    WithDecryption=True
                )
                self.mimecast_access_key = resp.get("Parameter").get("Value")

                resp = ps.get_parameter(
                    Name=self.authentication_details["PARAMETER_STORE_SECRET_KEY"],
                    WithDecryption=True
                )
                self.mimecast_secret_key = resp.get("Parameter").get("Value")

                resp = ps.get_parameter(
                    Name=self.authentication_details["PARAMETER_STORE_EMAIL_ADDRESS"],
                    WithDecryption=True
                )
                self.mimecast_email_address = resp.get("Parameter").get("Value")
            except Exception as e:
                log.error("Failed to assign Mimecast credentials from AWS Parameter Store")
                log.error(e)

    def get_email_address(self):
        return self.mimecast_email_address

    def get_app_id(self):
        return self.mimecast_app_id

    def get_app_key(self):
        return self.mimecast_app_key

    def get_access_key(self):
        return self.mimecast_access_key

    def get_secret_key(self):
        return self.mimecast_secret_key

    def get_source_details(self):
        return self.source_details

    def get_syslog_details(self):
        return self.syslog_details

    def get_logging_details(self):
        return self.logging_details

    def get_api_options(self):
        return self.api_options

    def get_s3_options(self):
        return self.s3_options


# This has to be at the end to avoid circular imports
from .logger import log  # noqa: E402
