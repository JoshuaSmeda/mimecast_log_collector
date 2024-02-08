import boto3
import os
import mimecast.Config

Config = mimecast.Config.Config()


def copy_to_s3(dir: str, file_name: str, path: str, s3_bucket: str) -> None:
    s3 = boto3.client("s3", region_name=Config.get_aws_options()["AWS_REGION"])
    s3.put_object(
        Bucket=s3_bucket,
        Key=f"{dir}/{file_name}",
        Body=open(f"{path}/{dir}/{file_name}", "rb")
    )
    os.remove(f"{path}/{dir}/{file_name}")
