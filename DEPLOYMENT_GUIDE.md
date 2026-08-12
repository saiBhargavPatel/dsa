# DSAHub — Render Deployment Guide (with Kong API Gateway)

This guide walks you through deploying the full DSAHub platform on Render, with **Kong**
as the public API gateway and the four FastAPI microservices as **private services**.

> **Architecture on Render:**
> - `kong-gateway` — public web service (receives all client traffic)
> - `auth-service`, `course-service`, `quiz-service`, `progress-service` — private services
>   (reachable only over Render's private network)
> - `dsa-frontend` — static site (serves the SPA, calls Kong cross-origin)
> - `dsa-postgres` — managed PostgreSQL
> - `dsa-redis` — managed Key Value (Redis-compatible)

---

## Prerequisites

1. **A GitHub account** and a Git repository with the DSAHub code pushed to it.
2. **A Render account** (https://render.com). The private services and Postgres require
   a paid plan — the `render.yaml` uses `starter` / `basic-256mb` which are the cheapest
   paid tiers.
3. **All code changes applied** — the files in this repo are already configured. Confirm
   you have the latest `render.yaml`, `kong/`, Dockerfiles, and `frontend/build.sh`.

---

## Step 1 — Push the repository to GitHub

If you haven't already, initialize Git and push:

```bash
cd /path/to/dsa
git init
git add .
git commit -m "Configure Kong gateway and Render deployment"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

> Make sure `.gitignore` excludes `.venv/`, `__pycache__/`, and `.env`. The included
> `.dockerignore` already handles Docker build context.

---

## Step 2 — Create a Render Blueprint from the repo

1. Log in to the [Render Dashboard](https://dashboard.render.com).
2. Click **New** → **Blueprint**.
3. Select your GitHub repository (`<your-user>/<your-repo>`).
4. Render detects the `render.yaml` file and shows a preview of all resources it will create:
   - **1 web service:** `kong-gateway`
   - **1 web (static) service:** `dsa-frontend`
   - **4 private services:** `auth-service`, `course-service`, `quiz-service`, `progress-service`
   - **1 keyvalue:** `dsa-redis`
   - **1 database:** `dsa-postgres`
5. Review the plan/region for each (the Blueprint sets `region: singapore` and paid plans
   for the private services + Postgres — adjust the region if you prefer another).
6. Click **Apply**.

Render begins provisioning all resources. This takes **5–10 minutes** on the first run
(Postgres needs to boot, images need to build, etc.).

---

## Step 3 — Wait for services to come up

Watch the Dashboard. Each service goes through **Building → Deploying → Live**.

### What to check in the logs:

**Postgres (`dsa-postgres`):**
- Should reach "Available" status. Note the internal connection string is auto-wired —
  you don't need to copy it.

**Redis (`dsa-redis`):**
- Should reach "Available" quickly. Connection string is auto-wired via `fromService`.

**Private services (auth, course, quiz, progress):**
- Each should log `Uvicorn running on http://0.0.0.0:10000` (Render sets `PORT=10000`
  by default for private services).
- The course and quiz services will auto-seed on first startup — you'll see seeding
  messages in their logs.
- If a service shows `OperationalError` / connection refused to Postgres on the very first
  boot, it's a startup race (the service booted before Postgres was ready). Render will
  auto-retry; it should recover within a minute or two.

**Kong (`kong-gateway`):**
- You should see the entrypoint log: `[kong-entrypoint] rendered declarative config -> /tmp/kong-rendered.yml`
- Kong starts in DB-less mode with the rendered config.
- The service gets a public URL like `https://kong-gateway-<random>.onrender.com`.

**Frontend (`dsa-frontend`):**
- The build command `bash build.sh` runs. Since `API_BASE_URL` is a placeholder on the
  first deploy, the SPA will default to same-origin (which won't work yet — we fix this
  in Step 4). This is expected.

---

## Step 4 — Wire the frontend to the Kong public URL  ⚠️ (critical)

The frontend SPA is on a **different origin** than Kong. It needs to know Kong's public URL.
This is the one manual step, because the Kong URL is only known after the first deploy.

### 4a. Copy the Kong public URL

1. In the Render Dashboard, click the **`kong-gateway`** service.
2. Copy its public URL from the top-left (e.g. `https://kong-gateway-ab12cd.onrender.com`).

### 4b. Set `API_BASE_URL` on the frontend

1. Click the **`dsa-frontend`** service.
2. Go to **Environment** in the left sidebar.
3. Find the `API_BASE_URL` env var and update its value to the Kong URL you copied:
   ```
   https://kong-gateway-ab12cd.onrender.com
   ```
   *(use your actual URL — do NOT add a trailing slash)*
4. Click **Save Changes**.

### 4c. Redeploy the frontend

Setting the env var triggers a redeploy automatically. If it doesn't, click **Manual Deploy** → **Deploy latest commit**.

When the build runs, `build.sh` will inject the URL into `config.js`:
```
[build.sh] Injecting API_BASE_URL=https://kong-gateway-ab12cd.onrender.com into config.js
```

### (Alternative) Update `render.yaml` permanently

To avoid doing this manually on every fresh Blueprint apply, edit `render.yaml` in the
repo and replace the placeholder value, then commit:

```yaml
  - type: web
    name: dsa-frontend
    ...
    envVars:
      - key: API_BASE_URL
        value: https://kong-gateway-ab12cd.onrender.com   # ← your real URL
```

---

## Step 5 — Verify the deployment

### 5a. Test the API through Kong

From your terminal, hit the Kong public URL directly:

```bash
KONG_URL=https://kong-gateway-ab12cd.onrender.com

# Health (no auth)
curl -s $KONG_URL/courses/topics | jq '.[0]'

# Register
curl -s -X POST $KONG_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"secret123"}' | jq

# Login and get a token
TOKEN=$(curl -s -X POST $KONG_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}' | jq -r .access_token)

# Authenticated request
curl -s $KONG_URL/progress/leaderboard \
  -H "Authorization: Bearer $TOKEN" | jq
```

If these return valid JSON, Kong is routing correctly to all backend services. 🎉

### 5b. Test the frontend

1. Open the `dsa-frontend` public URL (e.g. `https://dsa-frontend-ab12cd.onrender.com`)
   in your browser.
2. You should see the DSAHub home page with topic cards.
3. Click **Browse Courses** — topics should load (this confirms the SPA → Kong → course-service path works).
4. Register an account, open a lesson, take a quiz, check the leaderboard.

### 5c. Check CORS in the browser console

If API calls fail in the browser with a CORS error, verify:
- The Kong `cors` plugin is loaded (check Kong logs for `cors` plugin initialization).
- The browser is calling the Kong URL (not the static-site origin). Open DevTools → Network
  and confirm request URLs start with your `kong-gateway` URL.

---

## Step 6 — (Optional) Custom domains

To use your own domain (e.g. `dsa.yourdomain.com`):

1. **Frontend:** In the `dsa-frontend` service → **Settings** → **Custom Domains**, add
   your domain and add the CNAME record Render gives you to your DNS provider.
2. **Kong / API:** In the `kong-gateway` service → **Settings** → **Custom Domains**, add
   e.g. `api.yourdomain.com`.
3. Update `API_BASE_URL` on the frontend to the Kong custom domain and redeploy.

---

## How the Render config works (reference)

### Why private services?

The four FastAPI services are `type: pserv` (private service). They have **no public URL** —
they're reachable only by other Render services on the same private network. This means
the outside world can only reach your API through Kong, which is exactly the gateway
pattern. The services are protected from direct internet access.

### Why can't Kong hardcode `http://auth-service:4001`?

Render assigns each private service a hostname with a **random suffix**
(e.g. `auth-service-a1b2:10000`), not the bare service name. The exact hostname is only
known after the service is created. The `render.yaml` solves this with:

```yaml
- key: AUTH_SERVICE_HOSTPORT
  fromService:
    name: auth-service
    type: pserv
    property: hostport      # returns "auth-service-a1b2:10000" at runtime
```

Kong's `entrypoint.sh` reads these env vars at startup and substitutes them into `kong.yml`
(prepending `http://`), producing valid upstream URLs. This is why the Kong Dockerfile uses
an entrypoint script rather than baking the config at build time.

### Why do the Dockerfiles use `${PORT:-4001}`?

Render injects a `PORT` env var (default `10000` for private services). The Dockerfiles
use the shell form `CMD ["sh","-c","uvicorn ... --port ${PORT:-4001}"]` so the port expands
at runtime. The `${PORT:-4001}` means: use `$PORT` if set, otherwise fall back to 4001 for
local Docker Compose runs.

### Why is the admin API disabled?

`render.yaml` sets `KONG_ADMIN_LISTEN: "off"`. In DB-less mode, Kong doesn't need the admin
API, and exposing it publicly would let anyone reconfigure your gateway. It's a security
measure.

### Why is `API_BASE_URL` a two-step process?

The frontend needs Kong's public URL, but that URL doesn't exist until Kong is deployed.
So on the first deploy, `API_BASE_URL` is a placeholder; after Kong is live, you update it
and redeploy the frontend. If you already know your Kong URL (e.g. from a previous deploy),
you can set it correctly in `render.yaml` before the first apply and skip Step 4.

---

## Troubleshooting

### Kong returns 502 Bad Gateway / 503 Service Unavailable
- **Cause:** An upstream service is down, or the `*_HOSTPORT` env var is wrong/missing.
- **Fix:** Check the Kong logs for which upstream failed. Verify the private services are
  Live. In the Render Dashboard, check that the `AUTH_SERVICE_HOSTPORT` etc. env vars on
  `kong-gateway` resolved to real host:port values (they should show the suffixed hostname).

### Frontend loads but API calls fail (404 or CORS error)
- **Cause:** `API_BASE_URL` is not set or is wrong.
- **Fix:** Confirm `API_BASE_URL` on `dsa-frontend` matches the Kong public URL exactly
  (including `https://`, no trailing slash). Check the browser DevTools Network tab to see
  where requests are going. Redeploy the frontend after fixing.

### Progress service returns 503 "Auth service unavailable"
- **Cause:** The progress service can't reach the auth service, or the URL has no scheme.
- **Fix:** Check that `AUTH_SERVICE_URL` on `progress-service` is set via `fromService: hostport`.
  The `config.py` should prepend `http://` — verify in the progress service logs that the
  URL looks like `http://auth-service-xxxx:10000`. If it shows a bare `auth-service-xxxx:10000`,
  the config.py normalization didn't run (make sure you're running the updated image).

### Services crash-loop on first boot (Postgres connection refused)
- **Cause:** The service started before Postgres was ready (Render starts services in
  parallel; there's no `depends_on` like Docker Compose).
- **Fix:** This usually self-resolves — Render retries failed deploys. If it doesn't,
  trigger a manual redeploy of the affected service once Postgres shows "Available".

### Database is empty (no topics/quizzes)
- **Cause:** The course/quiz services only seed if their tables are empty *and* the DB
  connection succeeded on startup.
- **Fix:** Trigger a re-seed manually:
  ```bash
  curl -s -X POST $KONG_URL/courses/admin/seed
  curl -s -X POST $KONG_URL/quizzes/admin/seed
  ```

### Kong port / binding issues
- **Cause:** Kong was configured to listen on port 10000 (restricted on Render's private
  network) or the `PORT` env var conflicts.
- **Fix:** The `render.yaml` sets `PORT=8000` and `KONG_PROXY_LISTEN=0.0.0.0:8000`. Confirm
  these are set on the `kong-gateway` service. Kong should log `nginx: ... 0.0.0.0:8000`.

---

## Resource summary & cost notes

| Resource | Render type | Plan | Public? |
|----------|-------------|------|---------|
| kong-gateway | web service (Docker) | starter | ✅ Yes |
| dsa-frontend | static site | free | ✅ Yes |
| auth-service | private service (Docker) | starter | ❌ No |
| course-service | private service (Docker) | starter | ❌ No |
| quiz-service | private service (Docker) | starter | ❌ No |
| progress-service | private service (Docker) | starter | ❌ No |
| dsa-postgres | Postgres | basic-256mb | ❌ No |
| dsa-redis | Key Value | starter | ❌ No |

> The free static site will spin down after ~15 min of inactivity (cold start ~30s on next
> visit). The paid services stay up. If you want no cold starts on the API, keep
> `kong-gateway` on `starter` (or higher). Adjust plans in `render.yaml` as needed.

---

## Updating after deployment

When you push a new commit to `main`, Render auto-deploys all services
(`autoDeployTrigger: commit`). To deploy a single service only, use **Manual Deploy** in
that service's dashboard. Environment variable changes trigger a redeploy of the affected
service automatically.

---

## Need help?

- Architecture overview: see [README.md](README.md)
- Render Blueprint reference: https://render.com/docs/blueprint-spec
- Kong declarative config: https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/
