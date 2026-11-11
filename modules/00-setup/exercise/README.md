# Module 0 exercise: your first object

Put one of the IMDb files into the object storage, using Python.

This is the smallest version of what a data platform does all day: take a file from somewhere and store it in the lake, under a name that says what it is.

## What to do

Open [`upload_dataset.py`](upload_dataset.py) in your editor. It has three steps marked `TODO`. Complete them so that the script:

1. creates a bucket named `exercise`;
2. uploads `data/imdb/title.ratings.tsv.gz` to that bucket, under the key `imdb/title.ratings.tsv.gz`;
3. lists the objects in the bucket and prints each key with its size.

Edit the file in place. Your changes here do not affect the module checkpoint.

Run it as often as you like:

```
./course run python modules/00-setup/exercise/upload_dataset.py
```

## How you know it worked

The script prints the key and its size, about 8 MB:

```
imdb/title.ratings.tsv.gz  8.3 MB
```

Then open the console at http://localhost:9001/rustfs/console/. The `exercise` bucket is there, with a folder `imdb` and your file inside.

## What you need to know

The script uses `boto3`, the standard Python library for S3-compatible storage. It already creates the client for you:

```python
s3 = boto3.client("s3")
```

The address of the storage and your credentials come from the environment, so they are not written in the code. Three methods of the client are enough for this exercise:

| Method | What it does |
| --- | --- |
| `s3.create_bucket(Bucket=...)` | Creates a bucket |
| `s3.upload_file(Filename=..., Bucket=..., Key=...)` | Uploads a file from disk |
| `s3.list_objects_v2(Bucket=...)` | Returns a dictionary. Its `"Contents"` entry is a list with one dictionary per object, each with a `"Key"` and a `"Size"` in bytes |

## Things to try afterwards

- Run the script a second time. What happens at step 1, and why? Make the script work no matter how many times it runs. That is the idempotency you saw in the lab.
- Upload a second file under a different key and list the bucket again.
- Find your file in the console and look at its details.

## Stuck?

A reference solution is in [`../solution/`](../solution/). Reading it after a real attempt teaches more than reading it first.
