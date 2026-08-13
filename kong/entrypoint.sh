#!/bin/sh
# Kong declarative-config entrypoint.
#
# kong.yml uses __*_HOSTPORT__ placeholders because the upstream
# hostnames on Render's private network carry a random suffix
# (e.g. auth-service-ab1c) and are only known at runtime via the
# *_HOSTPORT env vars. We render the final config here, then start Kong.
set -eu

TEMPLATE="${KONG_DECLARATIVE_CONFIG:-/kong/declarative/kong.yml}"
RENDERED="/tmp/kong-rendered.yml"

# Default to localhost names for local docker-compose runs so the
# template works unchanged in both environments.
AUTH_SERVICE_HOSTPORT="${AUTH_SERVICE_HOSTPORT:-auth-service:4001}"
COURSE_SERVICE_HOSTPORT="${COURSE_SERVICE_HOSTPORT:-course-service:4002}"
QUIZ_SERVICE_HOSTPORT="${QUIZ_SERVICE_HOSTPORT:-quiz-service:4003}"
PROGRESS_SERVICE_HOSTPORT="${PROGRESS_SERVICE_HOSTPORT:-progress-service:4004}"

sed \
  -e "s|__AUTH_SERVICE_HOSTPORT__|${AUTH_SERVICE_HOSTPORT}|g" \
  -e "s|__COURSE_SERVICE_HOSTPORT__|${COURSE_SERVICE_HOSTPORT}|g" \
  -e "s|__QUIZ_SERVICE_HOSTPORT__|${QUIZ_SERVICE_HOSTPORT}|g" \
  -e "s|__PROGRESS_SERVICE_HOSTPORT__|${PROGRESS_SERVICE_HOSTPORT}|g" \
  "$TEMPLATE" > "$RENDERED"

export KONG_DECLARATIVE_CONFIG="$RENDERED"

echo "[kong-entrypoint] rendered declarative config -> $RENDERED"

# Warn if any placeholders were not substituted (e.g. a missing env var).
if grep -q "__.*_HOSTPORT__" "$RENDERED"; then
  echo "[kong-entrypoint] WARNING: unresolved __HOSTPORT__ placeholders remain in config"
else
  echo "[kong-entrypoint] all upstream hostports resolved successfully"
fi

exec docker-entrypoint.sh kong docker-start
