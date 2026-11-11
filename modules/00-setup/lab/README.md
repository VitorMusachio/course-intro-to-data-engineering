# Module 0 lab: start the environment

Follow the steps in order. Each one shows the command to run and what you should see. If something looks different, check the [troubleshooting section](../README.md#8-troubleshooting) of the lesson.

Run every command from the repository folder.

## Step 1: Get the repository

```
git clone https://github.com/VitorMusachio/course-intro-to-data-engineering.git
cd course-intro-to-data-engineering
```

On Windows, do this inside the Ubuntu terminal, in a folder under your Linux home.

## Step 2: Create your `.env` file

```
cp .env.example .env
```

The `.env` file holds the settings and credentials for your local environment. Open `.env.example` and read it: every variable has a comment explaining what it is for.

Git ignores `.env`, so it is never committed. This is a habit worth building now. In a real project, a committed credential is a security incident.

## Step 3: Check your machine

```
./course doctor
```

You should see a list of lines that start with `ok`, ending with:

```
Everything looks good. Next: ./course up
```

A line that starts with `FAIL` tells you what to fix. Fix it and run the command again.

## Step 4: Start the environment

```
./course up
```

The first time, Docker downloads the images and builds the toolbox. This takes a few minutes. When it finishes you see:

```
Ready.
  Object storage console: http://localhost:9001
  Stop everything with:   ./course down
```

Now look at what is running:

```
./course status
```

Two services are listed, `storage` and `toolbox`, both `healthy`.

## Step 5: Look at the object storage

Open http://localhost:9001 in your browser. This is the console of your object storage.

Sign in with the values of `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY` from your `.env` file.

The storage is empty. Object storage organizes files into **buckets**, which are top-level containers, a little like drives. Inside a bucket, each file is an **object**, identified by a **key**, which is its full name including any folders. There are no buckets yet. You create the first one in the exercise.

## Step 6: Download the datasets

```
./course data
```

This downloads seven files from IMDb, about 1.9 GB in total. Progress is printed for each file. When it finishes:

```
Done. Downloaded 7, already up to date 0.
```

The files are in `data/imdb/`. Look at them:

```
ls -lh data/imdb/
```

Now run the same command again:

```
./course data
```

```
Done. Downloaded 0, already up to date 7.
```

Nothing was downloaded the second time. The script recorded what it fetched and only downloads a file again if it changed on IMDb's side. A step that can be repeated safely, and does nothing when there is nothing to do, is called **idempotent**. You will see the word again: it is one of the most useful properties a data pipeline can have.

Which files are downloaded is not written in the script. It is declared in [`config/sources.yml`](../../../config/sources.yml). Open it. Each file has a short name and a description of what one row means. Later modules read this same file.

## Step 7: Take a first look at the data

The files are compressed text, with one row per line and tabs between columns. Look at the first rows of the ratings file:

```
./course run python -c "
import gzip
with gzip.open('data/imdb/title.ratings.tsv.gz', 'rt') as f:
    for _ in range(5):
        print(f.readline().rstrip())
"
```

You should see a header and four rows, similar to:

```
tconst	averageRating	numVotes
tt0000001	5.7	2100
tt0000002	5.5	290
tt0000003	6.4	2200
tt0000004	5.2	190
```

Your numbers will differ, because IMDb updates the data every day. `tconst` is IMDb's identifier for a title. It appears in every file and is how the files connect to each other.

That command ran inside the toolbox container, not on your machine. `./course run` is how you run any command there.

## Step 8: Run the checkpoint

```
./course check 0
```

The checkpoint tests that your environment meets the goals of this module. It ends with one line per goal:

```
pass  1. The base environment starts with one command.
pass  2. Every service in the base environment reports healthy.
pass  3. The object storage accepts a bucket, and an object can be written, read and deleted.
pass  4. Every declared dataset is downloaded and complete, so a second download fetches nothing.
pass  5. Starting the environment and downloading the data leaves nothing for git to commit.
pass  6. The .env file with your credentials is ignored by git and not committed.
skip  7. One command stops the environment and removes its containers. (checked by ./course down itself, which fails if a container is left behind)
pass  8. This checkpoint has one result for each of the nine criteria.
skip  9. The same checkpoint passes in continuous integration. (checked by the CI workflow on every pull request)
```

Seven lines say `pass` and two say `skip`. The two skipped goals cannot be tested from inside a running environment, and each line says where it is checked instead.

A line that says `FAIL` comes with a message above it that tells you what to do.

## Step 9: Do the exercise

Keep the environment running and go to the [exercise](../exercise/README.md).

## Step 10: Stop the environment

When you are done for the day:

```
./course down
```

```
Stopped. No course containers are left.
```

Your datasets and anything you stored in the object storage are kept. Next time, `./course up` starts in seconds, because the images are already on your machine.
