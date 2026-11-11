"""Steps 3 and 4: Spark writes Parquet through s3a, then creates an Iceberg
table, appends to it and reads an earlier snapshot.

Each step prints one line, "RESULT <step> pass|fail". The job always exits 0
so one failing step does not hide the others.
"""
import traceback

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("object-storage-experiment").getOrCreate()
state = {}


def step(name, fn):
    try:
        fn()
        print(f"RESULT {name} pass", flush=True)
    except Exception:  # noqa: BLE001 - report and continue
        traceback.print_exc()
        print(f"RESULT {name} fail", flush=True)


def parquet():
    path = "s3a://warehouse/exp/parquet"
    df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "v"])
    df.write.mode("overwrite").parquet(path)
    assert spark.read.parquet(path).count() == 2


def iceberg_write():
    spark.sql("CREATE NAMESPACE IF NOT EXISTS lake.exp")
    spark.sql("DROP TABLE IF EXISTS lake.exp.titles")
    spark.sql("CREATE TABLE lake.exp.titles (id BIGINT, v STRING) USING iceberg")
    spark.sql("INSERT INTO lake.exp.titles VALUES (1, 'a'), (2, 'b')")
    state["first_snapshot"] = spark.sql(
        "SELECT snapshot_id FROM lake.exp.titles.snapshots ORDER BY committed_at"
    ).first()[0]
    spark.sql("INSERT INTO lake.exp.titles VALUES (3, 'c'), (4, 'd')")
    assert spark.sql("SELECT count(*) FROM lake.exp.titles").first()[0] == 4


def iceberg_time_travel():
    snapshot = state["first_snapshot"]
    count = spark.sql(
        f"SELECT count(*) FROM lake.exp.titles VERSION AS OF {snapshot}"
    ).first()[0]
    assert count == 2, count


step("spark_parquet", parquet)
step("iceberg_write", iceberg_write)
step("iceberg_time_travel", iceberg_time_travel)
spark.stop()
