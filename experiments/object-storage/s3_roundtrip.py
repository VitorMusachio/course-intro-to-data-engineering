"""Step 1: create a bucket, write, read and delete an object over the S3 API.

Usage: s3_roundtrip.py wait | bucket | roundtrip
"""
import os
import sys
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

BUCKET = os.environ["S3_BUCKET"]


def client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
        config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 1}),
    )


def wait(seconds=120):
    """Poll until the service answers an authenticated S3 call."""
    start = time.time()
    last = None
    while time.time() - start < seconds:
        try:
            client().list_buckets()
            print(f"ready after {time.time() - start:.1f}s")
            return
        except Exception as exc:  # noqa: BLE001 - any failure means "not ready yet"
            last = exc
            time.sleep(1)
    raise SystemExit(f"not ready after {seconds}s: {last!r}")


def bucket():
    try:
        client().create_bucket(Bucket=BUCKET)
        print("bucket created")
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print("bucket already exists")
        else:
            raise


def roundtrip():
    s3 = client()
    key = "exp/roundtrip.txt"
    body = b"hello object storage"
    s3.put_object(Bucket=BUCKET, Key=key, Body=body)
    assert s3.get_object(Bucket=BUCKET, Key=key)["Body"].read() == body
    listed = [o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix="exp/").get("Contents", [])]
    assert key in listed, listed
    s3.delete_object(Bucket=BUCKET, Key=key)
    after = [o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix="exp/").get("Contents", [])]
    assert key not in after, after
    print("round trip ok")


if __name__ == "__main__":
    {"wait": wait, "bucket": bucket, "roundtrip": roundtrip}[sys.argv[1]]()
