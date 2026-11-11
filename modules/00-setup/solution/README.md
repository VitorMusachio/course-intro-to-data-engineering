# Module 0 solution

[`upload_dataset.py`](upload_dataset.py) is one way to complete the exercise. Yours can look different and still be right: what matters is that the file ends up in the bucket and the script prints it.

Run it with:

```
./course run python modules/00-setup/solution/upload_dataset.py
```

## What to notice

**It can run any number of times.** Creating a bucket that already exists is an error. The solution checks for that specific error and carries on, and lets any other error stop the script. Catching only the error you expect matters: a script that ignores every error hides real problems, such as wrong credentials.

**Uploading the same key twice replaces the object.** Object storage has no "file already exists" error for objects. The last write wins. That makes uploads naturally repeatable, and it also means a careless write can silently replace good data. Later modules deal with that.

**The key looks like a path, but it is only a name.** `imdb/title.ratings.tsv.gz` is a single string. The console shows `imdb` as a folder because the name contains a slash. There are no real folders in object storage, which is why you never had to create one.

**Nothing in the code says where the storage is.** The address and the credentials come from the environment. The same script would work against Amazon S3 by changing the environment and not the code.
