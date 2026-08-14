#!/bin/sh

# =========================================================
# Kong declarative-config entrypoint
#
# Supports:
#   1. Local Docker Compose
#   2. Render Free deployment
#
# Local:
#   auth-service:4001
#   course-service:4002
#   quiz-service:4003
#   progress-service:4004
#
# Render:
#   https://auth-service-xxxx.onrender.com
#   https://course-service-xxxx.onrender.com
#   etc.
# =========================================================

set -eu

TEMPLATE="${KONG_DECLARATIVE_CONFIG:-/kong/declarative/kong.yml}"
RENDERED="/tmp/kong-rendered.yml"


# =========================================================
# Default values for LOCAL Docker Compose
# =========================================================

AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://auth-service:4001}"
COURSE_SERVICE_URL="${COURSE_SERVICE_URL:-http://course-service:4002}"
QUIZ_SERVICE_URL="${QUIZ_SERVICE_URL:-http://quiz-service:4003}"
PROGRESS_SERVICE_URL="${PROGRESS_SERVICE_URL:-http://progress-service:4004}"


# =========================================================
# Render Kong configuration
# =========================================================

sed \
  -e "s|__AUTH_SERVICE_URL__|${AUTH_SERVICE_URL}|g" \
  -e "s|__COURSE_SERVICE_URL__|${COURSE_SERVICE_URL}|g" \
  -e "s|__QUIZ_SERVICE_URL__|${QUIZ_SERVICE_URL}|g" \
  -e "s|__PROGRESS_SERVICE_URL__|${PROGRESS_SERVICE_URL}|g" \
  "$TEMPLATE" > "$RENDERED"


# Tell Kong to use the rendered configuration
export KONG_DECLARATIVE_CONFIG="$RENDERED"


echo "[kong-entrypoint] rendered declarative config -> $RENDERED"


# =========================================================
# Validate that no placeholders remain
# =========================================================

if grep -q "__.*_URL__" "$RENDERED"; then
    echo "[kong-entrypoint] WARNING: unresolved __URL__ placeholders remain in config"
    grep "__.*_URL__" "$RENDERED" || true
else
    echo "[kong-entrypoint] all upstream URLs resolved successfully"
fi


# =========================================================
# Start Kong
# =========================================================

exec /docker-entrypoint.sh kong docker-start