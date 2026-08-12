# Shared constants used across microservices.
#
# Note: JWT_SECRET is intentionally NOT defined here. Each environment
# provides it via the JWT_SECRET env var:
#   - Locally:  set in docker-compose.yml (dev value) or your shell
#   - Render:   generated automatically (generateValue: true in render.yaml)
# The auth service reads it from settings.jwt_secret (see auth-service/config.py).

API_PREFIX = "/api"
