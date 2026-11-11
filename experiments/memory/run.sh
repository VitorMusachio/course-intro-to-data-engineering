#!/usr/bin/env bash
# Experiment B: how much memory does the course need?
#
#   ./run.sh base | lakehouse | datahub
#
# Starts one scenario, samples `docker stats` every few seconds while it
# works, and reports the peak per container and the peak of the total.
# It always exits 0: a scenario that fails to start is a finding.
set -uo pipefail

SCENARIO="${1:?usage: run.sh base|lakehouse|datahub}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
STORAGE_EXP="$ROOT/experiments/object-storage"

NET=exp
BUCKET=warehouse
ACCESS_KEY=GK0123456789abcdef01234567
SECRET_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
REGION=us-east-1
ENDPOINT=http://storage:9000

RUSTFS_IMAGE=rustfs/rustfs:1.0.0
SPARK_IMAGE=apache/spark:4.0.1
ICEBERG_VERSION=1.10.1
REST_IMAGE=apache/iceberg-rest-fixture:1.10.1
TRINO_IMAGE=trinodb/trino:480

SAMPLES=/tmp/samples.txt
NOTES=()

note() { NOTES+=("$*"); echo "NOTE $*"; }

# ---------------------------------------------------------------- sampler --

start_sampling() {
  : > "$SAMPLES"
  touch /tmp/sampling
  (
    while [ -f /tmp/sampling ]; do
      now=$(date +%s)
      docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' 2>/dev/null \
        | awk -v t="$now" '{print t, $1, $2}' >> "$SAMPLES"
      sleep 3
    done
  ) &
  SAMPLER=$!
}

stop_sampling() {
  rm -f /tmp/sampling
  wait "$SAMPLER" 2>/dev/null || true
}

report() {
  echo "::group::memory report"
  awk '
    function mib(v) {
      if (v ~ /GiB$/) return substr(v, 1, length(v) - 3) * 1024
      if (v ~ /MiB$/) return substr(v, 1, length(v) - 3) + 0
      if (v ~ /KiB$/) return substr(v, 1, length(v) - 3) / 1024
      return 0
    }
    {
      m = mib($3)
      if (m > peak[$2]) peak[$2] = m
      total[$1] += m
    }
    END {
      for (t in total) if (total[t] > top) top = total[t]
      for (c in peak) printf "PEAK %s %d\n", c, peak[c]
      printf "PEAK_TOTAL %d\n", top
    }
  ' "$SAMPLES" | sort > /tmp/report.txt
  cat /tmp/report.txt
  echo "samples: $(cut -d' ' -f1 "$SAMPLES" | sort -u | wc -l)"
  echo "::endgroup::"
  echo "::notice title=$SCENARIO memory::$(tr '\n' ';' < /tmp/report.txt) notes: ${NOTES[*]:-none}"
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    {
      echo "### $SCENARIO"
      echo
      echo "| Container | Peak memory (MiB) |"
      echo "| --- | --- |"
      awk '$1 == "PEAK" {printf "| %s | %s |\n", $2, $3}' /tmp/report.txt
      awk '$1 == "PEAK_TOTAL" {printf "| **all containers, same moment** | **%s** |\n", $2}' /tmp/report.txt
      echo
      for n in "${NOTES[@]:-}"; do [ -n "$n" ] && echo "- $n"; done
      echo
    } >> "$GITHUB_STEP_SUMMARY"
  fi
}

# ------------------------------------------------------------------ pieces --

toolbox() {
  docker run --rm --network "$NET" \
    -e S3_ENDPOINT="$ENDPOINT" -e S3_BUCKET="$BUCKET" \
    -e AWS_ACCESS_KEY_ID="$ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$SECRET_KEY" \
    -e AWS_REGION="$REGION" \
    -v "$STORAGE_EXP:/exp:ro" course-toolbox "$@"
}

start_storage() {
  docker network create "$NET" >/dev/null 2>&1 || true
  docker build --quiet --tag course-toolbox "$ROOT/docker/toolbox" >/dev/null
  docker run -d --name storage --network "$NET" \
    -e RUSTFS_ACCESS_KEY="$ACCESS_KEY" -e RUSTFS_SECRET_KEY="$SECRET_KEY" \
    -e RUSTFS_VOLUMES=/data -e RUSTFS_ADDRESS=0.0.0.0:9000 \
    "$RUSTFS_IMAGE"
  toolbox python /exp/s3_roundtrip.py wait
  toolbox python /exp/s3_roundtrip.py bucket
}

# --------------------------------------------------------------- scenarios --

scenario_base() {
  start_storage
  start_sampling
  # The toolbox stays up for the whole measurement, as it would while a
  # learner works through a lab.
  docker run -d --name toolbox --network "$NET" course-toolbox sleep 300
  for _ in $(seq 1 20); do toolbox python /exp/s3_roundtrip.py roundtrip >/dev/null; done
  sleep 30
  stop_sampling
}

scenario_lakehouse() {
  start_storage
  docker run -d --name rest --network "$NET" \
    -e AWS_ACCESS_KEY_ID="$ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$SECRET_KEY" -e AWS_REGION="$REGION" \
    -e CATALOG_WAREHOUSE="s3://$BUCKET/iceberg" \
    -e CATALOG_IO__IMPL=org.apache.iceberg.aws.s3.S3FileIO \
    -e CATALOG_S3_ENDPOINT="$ENDPOINT" \
    -e CATALOG_S3_PATH__STYLE__ACCESS=true \
    "$REST_IMAGE"
  mkdir -p /tmp/trino-catalog
  cat > /tmp/trino-catalog/lake.properties <<PROPS
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://rest:8181
fs.native-s3.enabled=true
s3.endpoint=$ENDPOINT
s3.region=$REGION
s3.path-style-access=true
s3.aws-access-key=$ACCESS_KEY
s3.aws-secret-key=$SECRET_KEY
PROPS
  docker run -d --name trino --network "$NET" \
    -v /tmp/trino-catalog:/etc/trino/catalog:ro "$TRINO_IMAGE"
  for _ in $(seq 1 120); do
    docker exec trino trino --execute "SELECT 1" >/dev/null 2>&1 && break
    sleep 2
  done
  echo "trino jvm settings:"; docker exec trino cat /etc/trino/jvm.config 2>/dev/null | grep -i -E "Xmx|RAMPercentage" || true

  start_sampling
  docker run --name spark --network "$NET" --user root \
    -e AWS_ACCESS_KEY_ID="$ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$SECRET_KEY" -e AWS_REGION="$REGION" \
    -v "$HERE:/mem:ro" "$SPARK_IMAGE" \
    /opt/spark/bin/spark-submit \
      --conf spark.jars.ivy=/tmp/ivy \
      --packages "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:$ICEBERG_VERSION,org.apache.iceberg:iceberg-aws-bundle:$ICEBERG_VERSION" \
      --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
      --conf spark.sql.catalog.lake=org.apache.iceberg.spark.SparkCatalog \
      --conf spark.sql.catalog.lake.type=rest \
      --conf spark.sql.catalog.lake.uri=http://rest:8181 \
      --conf spark.sql.catalog.lake.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
      --conf spark.sql.catalog.lake.s3.endpoint="$ENDPOINT" \
      --conf spark.sql.catalog.lake.s3.path-style-access=true \
      --conf spark.ui.enabled=false \
      /mem/workload.py > /tmp/spark.log 2>&1
  if grep -q "^WORKLOAD ok" /tmp/spark.log; then
    note "Spark workload completed (10 million rows written and aggregated, default 1 GB driver)"
  else
    note "Spark workload FAILED"
    grep -E "Exception|Error|OutOfMemory" /tmp/spark.log | grep -v -E "^[[:space:]]+at " | head -15
  fi
  count="$(docker exec trino trino --execute "SELECT count(*) FROM lake.exp.big" 2>&1 | tr -d '"' | tail -1)"
  docker exec trino trino --execute "SELECT bucket, count(*), approx_distinct(label) FROM lake.exp.big GROUP BY bucket ORDER BY 2 DESC LIMIT 5" >/dev/null 2>&1
  note "Trino counted $count rows and ran an aggregation over them"
  sleep 10
  stop_sampling
}

scenario_datahub() {
  python3 -m pip install --quiet --upgrade acryl-datahub 2>&1 | tail -2
  note "DataHub CLI $(datahub version 2>/dev/null | head -1 | tr -s ' ')"
  start_sampling
  if timeout 1200 datahub docker quickstart > /tmp/datahub.log 2>&1; then
    note "quickstart reached healthy"
    if timeout 600 datahub docker ingest-sample-data >> /tmp/datahub.log 2>&1; then
      note "sample metadata ingested"
    else
      note "sample metadata ingestion FAILED"
    fi
    sleep 60
  else
    note "quickstart FAILED to become healthy"
    tail -30 /tmp/datahub.log
  fi
  stop_sampling
  docker ps --format '{{.Names}}  {{.Image}}'
}

echo "::group::scenario $SCENARIO"
"scenario_$SCENARIO"
echo "::endgroup::"
report
exit 0
