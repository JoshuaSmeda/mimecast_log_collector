import boto3


def copy_to_s3(dir: str, file_name: str, path: str, s3_bucket: str) -> None:
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=s3_bucket,
        Key=f"{dir}/{file_name}",
        Body=open(f"{path}/{dir}/{file_name}", "rb")
    )
