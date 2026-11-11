"""Module 0 exercise, reference solution.

Creates a bucket, uploads one IMDb file to it and lists what the bucket holds.
It can be run any number of times.

    ./course run python modules/00-setup/solution/upload_dataset.py
"""

import boto3
from botocore.exceptions import ClientError

BUCKET = "exercise"
LOCAL_FILE = "data/imdb/title.ratings.tsv.gz"
KEY = "imdb/title.ratings.tsv.gz"

# The storage address and your credentials come from the environment.
s3 = boto3.client("s3")

# Step 1: create the bucket. If it is already there, that is fine. Any other
# error, such as wrong credentials, should still stop the script.
try:
    s3.create_bucket(Bucket=BUCKET)
    print(f"created bucket {BUCKET}")
except ClientError as error:
    if error.response["Error"]["Code"] not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
        raise
    print(f"bucket {BUCKET} already exists")

# Step 2: upload the file. Uploading to a key that exists replaces the object.
s3.upload_file(Filename=LOCAL_FILE, Bucket=BUCKET, Key=KEY)
print(f"uploaded {LOCAL_FILE}")

# Step 3: list what the bucket holds.
response = s3.list_objects_v2(Bucket=BUCKET)
for item in response.get("Contents", []):
    print(f"{item['Key']}  {item['Size'] / 1024 / 1024:.1f} MB")
