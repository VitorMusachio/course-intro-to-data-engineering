"""A small but real lakehouse workload, used only to see how much memory the
engines take while working: write ten million rows to an Iceberg table, then
aggregate them into a second table.
"""
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("memory-experiment").getOrCreate()

spark.sql("CREATE NAMESPACE IF NOT EXISTS lake.exp")
rows = spark.range(0, 10_000_000).selectExpr(
    "id",
    "id % 1000 AS bucket",
    "CAST(rand() * 100 AS INT) AS value",
    "uuid() AS label",
)
rows.writeTo("lake.exp.big").createOrReplace()

spark.sql(
    """
    SELECT bucket, count(*) AS n, avg(value) AS mean_value
    FROM lake.exp.big
    GROUP BY bucket
    """
).writeTo("lake.exp.by_bucket").createOrReplace()

assert spark.table("lake.exp.big").count() == 10_000_000
assert spark.table("lake.exp.by_bucket").count() == 1000
print("WORKLOAD ok", flush=True)
spark.stop()
