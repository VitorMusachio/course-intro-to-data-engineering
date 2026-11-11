"""Module 0 exercise: put one of the IMDb files into the object storage.

Complete the three steps marked TODO, then run:

    ./course run python modules/00-setup/exercise/upload_dataset.py

The instructions are in README.md, next to this file.
"""

import boto3

BUCKET = "exercise"
LOCAL_FILE = "data/imdb/title.ratings.tsv.gz"
KEY = "imdb/title.ratings.tsv.gz"

# The storage address and your credentials come from the environment.
s3 = boto3.client("s3")

# TODO 1: create the bucket named BUCKET.
print("TODO 1: create the bucket")

# TODO 2: upload LOCAL_FILE to the bucket, under the key KEY.
print("TODO 2: upload the file")

# TODO 3: list the objects in the bucket. For each one, print its key and
# its size in megabytes, like this:
#   imdb/title.ratings.tsv.gz  8.3 MB
print("TODO 3: list the objects")
