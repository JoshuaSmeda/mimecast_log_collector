import boto3
import botocore
import mimecast.Config
from mimecast.logger import log

Config = mimecast.Config.Config()


def get_checkpoint(param: str) -> str:
    ps = boto3.client("ssm", region_name=Config.get_aws_options()["AWS_REGION"])
    try:
        response = ps.get_parameter(
            Name=param,
            WithDecryption=True
        )
        if response.get("Parameter"):
            if response.get("Parameter").get("Value") == "INITVALUE":
                return ""
            else:
                return response.get("Parameter").get("Value")
        else:
            return ""
    # We may need to handle this error differently. Just catching it for now.
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ParameterNotFound":
            return ""
    except Exception as e:
        log.error(f"Error retrieving checkpoint - {e}")
        return ""


def put_checkpoint(param: str, data: str) -> bool:
    ps = boto3.client("ssm", region_name=Config.get_aws_options()["AWS_REGION"])
    try:
        response = ps.put_parameter(
            Name=param,
            Type="String",
            Value=data,
            Overwrite=True
        )
        if response.get("Version"):
            return True
        else:
            log.error(f"Unable to update checkpoint {param} with {data}")
            return False
    except Exception as e:
        log.error(f"Error updating checkpoint - {e}")
        return False
