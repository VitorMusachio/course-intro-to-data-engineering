#!/usr/bin/env bash
# Experiment A: is this object storage a workable base for the course?
#
#   ./run.sh seaweedfs | garage | rustfs
#
# Runs six steps against one candidate and prints one line per result:
#   RESULT <step> pass|fail
# plus a few measurements. It always exits 0: a failing step is a finding,
# not an error. Every value below is for a throwaway local test.
set -uo pipefail

CANDIDATE="${1:?usage: run.sh seaweedfs|garage|rustfs}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

NET=exp
BUCKET=warehouse
ACCESS_KEY=GK0123456789abcdef01234567
SECRET_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
REGION=us-east-1

SPARK_IMAGE=apache/spark:4.0.1
ICEBERG_VERSION=1.10.1
REST_IMAGE=apache/iceberg-rest-fixture:1.10.1
TRINO_IMAGE=trinodb/trino:480
HADOOP_AWS_VERSION=3.4.1

RESULTS=()

result() { # name status
  RESULTS+=("$1 $2")
  echo "RESULT $1 $2"
  echo "::notice title=$CANDIDATE::$1 $2"
}

measure() { # name value
  RESULTS+=("$1 $2")
  echo "MEASURE $1 $2"
  echo "::notice title=$CANDIDATE::$1 $2"
}

toolbox() {
  docker run --rm --network "$NET" \
    -e S3_ENDPOINT="$ENDPOINT" -e S3_BUCKET="$BUCKET" \
    -e AWS_ACCESS_KEY_ID="$ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$SECRET_KEY" \
    -e AWS_REGION="$REGION" \
    -v "$HERE:/exp:ro" course-toolbox "$@"
}

# ---------------------------------------------------------------- storage --

start_seaweedfs() {
  STORAGE_IMAGE=chrislusf/seaweedfs:4.53
  ENDPOINT=http://storage:8333
  docker run -d --name storage --network "$NET" \
    -v "$HERE/seaweedfs-s3.json:/etc/seaweedfs/s3.json:ro" \
    "$STORAGE_IMAGE" server -dir=/data -ip.bind=0.0.0.0 -s3 -s3.config=/etc/seaweedfs/s3.json
}

start_garage() {
  STORAGE_IMAGE=dxflrs/garage:v2.3.0
  ENDPOINT=http://storage:3900
  sed "s/__RPC_SECRET__/$(openssl rand -hex 32)/" "$HERE/garage.toml" > /tmp/garage.toml
  docker run -d --name storage --network "$NET" \
    -v /tmp/garage.toml:/etc/garage.toml:ro \
    "$STORAGE_IMAGE"
  # A Garage node accepts no writes until it has a layout.
  local node=""
  for _ in $(seq 1 30); do
    node="$(docker exec storage /garage status 2>/dev/null | awk '/NO ROLE ASSIGNED/{print $1; exit}')"
    [ -n "$node" ] && break
    sleep 1
  done
  echo "garage node: ${node:-<none found>}"
  docker exec storage /garage status || true
  docker exec storage /garage layout assign -z dc1 -c 1G "$node" || true
  docker exec storage /garage layout apply --version 1 || true
  docker exec storage /garage key import --yes -n course "$ACCESS_KEY" "$SECRET_KEY" \
    || docker exec storage /garage key import --yes "$ACCESS_KEY" "$SECRET_KEY" -n course || true
  docker exec storage /garage bucket create "$BUCKET" || true
  docker exec storage /garage bucket allow --read --write --owner "$BUCKET" --key "$ACCESS_KEY" || true
  docker exec storage /garage key allow --create-bucket "$ACCESS_KEY" || true
}

start_rustfs() {
  STORAGE_IMAGE=rustfs/rustfs:1.0.0
  ENDPOINT=http://storage:9000
  docker run -d --name storage --network "$NET" \
    -e RUSTFS_ACCESS_KEY="$ACCESS_KEY" -e RUSTFS_SECRET_KEY="$SECRET_KEY" \
    -e RUSTFS_VOLUMES=/data -e RUSTFS_ADDRESS=0.0.0.0:9000 \
    "$STORAGE_IMAGE"
}

# ------------------------------------------------------------------- run --

docker network create "$NET" >/dev/null 2>&1 || true
docker build --quiet --tag course-toolbox "$ROOT/docker/toolbox" >/dev/null

echo "::group::start $CANDIDATE"
started=$(date +%s)
"start_$CANDIDATE"
if toolbox python /exp/s3_roundtrip.py wait; then
  measure startup_seconds "$(( $(date +%s) - started ))"
  result storage_starts pass
else
  result storage_starts fail
fi
docker logs storage 2>&1 | tail -30
echo "::endgroup::"

echo "::group::step 2: S3 round trip"
toolbox python /exp/s3_roundtrip.py bucket
if toolbox python /exp/s3_roundtrip.py roundtrip; then result s3_roundtrip pass; else result s3_roundtrip fail; fi
echo "::endgroup::"

echo "::group::iceberg REST catalog"
docker run -d --name rest --network "$NET" \
  -e AWS_ACCESS_KEY_ID="$ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$SECRET_KEY" -e AWS_REGION="$REGION" \
  -e CATALOG_WAREHOUSE="s3://$BUCKET/iceberg" \
  -e CATALOG_IO__IMPL=org.apache.iceberg.aws.s3.S3FileIO \
  -e CATALOG_S3_ENDPOINT="$ENDPOINT" \
  -e CATALOG_S3_PATH__STYLE__ACCESS=true \
  "$REST_IMAGE"
toolbox python - <<'PY' || true
import time, urllib.request
for _ in range(90):
    try:
        urllib.request.urlopen("http://rest:8181/v1/config", timeout=2)
        print("rest catalog ready")
        break
    except Exception as exc:
        last = exc
        time.sleep(1)
else:
    print("rest catalog not ready:", repr(last))
PY
echo "::endgroup::"

echo "::group::steps 3 and 4: Spark, Parquet and Iceberg"
docker run --rm --network "$NET" --user root \
  -e AWS_ACCESS_KEY_ID="$ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$SECRET_KEY" -e AWS_REGION="$REGION" \
  -v "$HERE:/exp:ro" "$SPARK_IMAGE" \
  /opt/spark/bin/spark-submit \
    --conf spark.jars.ivy=/tmp/ivy \
    --packages "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:$ICEBERG_VERSION,org.apache.iceberg:iceberg-aws-bundle:$ICEBERG_VERSION,org.apache.hadoop:hadoop-aws:$HADOOP_AWS_VERSION" \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.lake=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.lake.type=rest \
    --conf spark.sql.catalog.lake.uri=http://rest:8181 \
    --conf spark.sql.catalog.lake.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
    --conf spark.sql.catalog.lake.s3.endpoint="$ENDPOINT" \
    --conf spark.sql.catalog.lake.s3.path-style-access=true \
    --conf spark.hadoop.fs.s3a.endpoint="$ENDPOINT" \
    --conf spark.hadoop.fs.s3a.endpoint.region="$REGION" \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
    --conf spark.hadoop.fs.s3a.access.key="$ACCESS_KEY" \
    --conf spark.hadoop.fs.s3a.secret.key="$SECRET_KEY" \
    --conf spark.ui.enabled=false \
    /exp/spark_job.py 2>&1 | tee /tmp/spark.log | grep -v -E ' (INFO|WARN) ' | tail -80
echo "--- first errors reported by Spark"
grep -E "Exception|Caused by|Error" /tmp/spark.log | grep -v -E "^[[:space:]]+at | INFO | WARN " | head -25
echo "--- catalog log, errors only"
docker logs rest 2>&1 | grep -E "Exception|Caused by|ERROR|Status Code|status code" | grep -v -E "^[[:space:]]+at " | head -25
echo "--- storage log, last lines"
docker logs storage 2>&1 | tail -25
echo "::endgroup::"
for step in spark_parquet iceberg_write iceberg_time_travel; do
  status="$(grep -E "^RESULT $step " /tmp/spark.log | awk '{print $3}' | tail -1)"
  result "$step" "${status:-fail}"
done

echo "::group::step 5: Trino"
mkdir -p /tmp/trino-catalog
cat > /tmp/trino-catalog/lake.properties <<EOF
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://rest:8181
fs.native-s3.enabled=true
s3.endpoint=$ENDPOINT
s3.region=$REGION
s3.path-style-access=true
s3.aws-access-key=$ACCESS_KEY
s3.aws-secret-key=$SECRET_KEY
EOF
docker run -d --name trino --network "$NET" \
  -v /tmp/trino-catalog:/etc/trino/catalog:ro "$TRINO_IMAGE"
ready=no
for _ in $(seq 1 120); do
  if docker exec trino trino --execute "SELECT 1" >/dev/null 2>&1; then ready=yes; break; fi
  sleep 2
done
echo "trino ready: $ready"
count="$(docker exec trino trino --execute "SELECT count(*) FROM lake.exp.titles" 2>&1 | tr -d '"' | tail -1)"
echo "trino read count: $count"
if [ "$count" = "4" ]; then result trino_reads pass; else result trino_reads fail; fi
if docker exec trino trino --execute "CREATE TABLE lake.exp.from_trino AS SELECT * FROM lake.exp.titles" 2>&1 | tail -3 \
   && [ "$(docker exec trino trino --execute "SELECT count(*) FROM lake.exp.from_trino" 2>&1 | tr -d '"' | tail -1)" = "4" ]; then
  result trino_writes pass
else
  result trino_writes fail
fi
docker logs trino 2>&1 | grep -E "ERROR|Exception" | tail -15
echo "::endgroup::"

echo "::group::step 6: measurements"
measure storage_image "$STORAGE_IMAGE"
measure storage_image_mb "$(docker image inspect "$STORAGE_IMAGE" --format '{{.Size}}' | awk '{printf "%d", $1/1024/1024}')"
measure storage_memory "$(docker stats --no-stream --format '{{.MemUsage}}' storage | awk '{print $1}')"
measure storage_digest "$(docker image inspect "$STORAGE_IMAGE" --format '{{index .RepoDigests 0}}' 2>/dev/null)"
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}'
echo "::endgroup::"

echo "::notice title=$CANDIDATE summary::$(printf '%s; ' "${RESULTS[@]}")"

echo
echo "== $CANDIDATE =="
printf '%s\n' "${RESULTS[@]}"
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "### $CANDIDATE"
    echo
    echo "| Item | Value |"
    echo "| --- | --- |"
    for line in "${RESULTS[@]}"; do echo "| ${line%% *} | ${line#* } |"; done
    echo
  } >> "$GITHUB_STEP_SUMMARY"
fi
exit 0
