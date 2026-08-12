# 🧠 DSAHub — Microservice-Based DSA Learning Platform

A fully functional, production-architected learning platform for **Data Structures & Algorithms**, built as a microservices application. Students can register, browse 12 DSA topics with 28 in-depth lessons, take quizzes, track progress, and compete on a leaderboard.

![Architecture](https://img.shields.io/badge/architecture-microservices-blue) ![Gateway](https://img.shields.io/badge/gateway-Kong-0033A0) ![Tests](https://img.shields.io/badge/tests-31%2F31%20passing-brightgreen)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start (Docker)](#quick-start-docker)
- [Deploying to Render](#deploying-to-render)
- [Running Locally (Without Docker)](#running-locally-without-docker)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [DSA Content](#dsa-content)
- [Testing](#testing)
- [Features](#features)
- [Environment Variables](#environment-variables)

---

## Overview

DSAHub is designed to demonstrate a real microservices architecture while providing genuine educational value. Each service is independently deployable, has its own database tables, and communicates through the **Kong API gateway**.

**What students can do:**
- 🔐 Register / login with JWT authentication
- 📚 Browse 12 DSA topics (Arrays → Advanced Graphs)
- 📖 Read 28 in-depth lessons with code examples, complexity tables, and visual explanations
- 📝 Take auto-graded quizzes with detailed explanations
- 📊 Track lesson completion and quiz scores
- 🏆 View a global leaderboard

---

## Architecture

```
                        ┌────────────────────────────────────┐
                        │        Web UI (SPA)                 │
                        │  HTML/CSS/JS — Render static site    │
                        │  (separate origin, calls Kong)       │
                        └────────────────┬───────────────────┘
                                         │ HTTPS (CORS)
                        ┌────────────────▼───────────────────┐
                        │     Kong API Gateway (public)       │
                        │   DB-less / declarative config       │
                        │   Routes /auth /courses /quizzes     │
                        │   /progress  +  CORS plugin          │
                        └──┬──────┬──────┬──────┬─────────────┘
                           │      │      │      │
                    ┌──────▼┐ ┌───▼───┐ ┌▼─────┐ ┌▼──────────┐
                    │  Auth  │ │Course │ │ Quiz │ │ Progress  │
                    │Service │ │Service│ │Service│ │  Service  │
                    │FastAPI │ │FastAPI│ │FastAPI│ │  FastAPI  │
                    └───┬────┘ └───┬───┘ └──┬───┘ └────┬──────┘
                        │          │        │          │
                    ┌───┴──────────┴────────┴──────────┴───┐
                    │     PostgreSQL (Render Postgres)       │
                    │     Shared DB, per-service tables       │
                    └────────────────────────────────────────┘
                    ┌───┴──────────┴────────┴──────────┴───┐
                    │     Redis (Render Key Value)           │
                    │     Caching + token blacklist          │
                    └────────────────────────────────────────┘
```

On **Render**, the four FastAPI services are **private services** (`pserv`) — they are
not reachable from the public internet. Kong is the single **public web service** that
receives all client traffic and proxies to the private services over Render's private
network. The SPA is a **static site** on its own origin and calls the Kong public URL
directly (Kong's CORS plugin permits the cross-origin request).

### Service Responsibilities

| Service | Type | Responsibility |
|---------|------|---------------|
| **Frontend (SPA)** | Static site | Vanilla-JS single-page app; calls Kong public URL |
| **Kong Gateway** | Public web service | Reverse proxy, CORS, request routing, rate-limiting ready |
| **Auth Service** | Private service | User registration, login, JWT issuance, token verification |
| **Course Service** | Private service | DSA topics, lessons, content delivery, search |
| **Quiz Service** | Private service | Quiz questions, answer submission, auto-grading |
| **Progress Service** | Private service | Lesson completion tracking, quiz scores, leaderboard |
| **PostgreSQL** | Render Postgres | Shared database (each service owns its own tables) |
| **Redis** | Render Key Value | Response caching, auth token blacklist, token verification cache |

### Inter-Service Communication
- **Browser → Kong:** HTTPS to the Kong public URL; CORS enabled via Kong plugin
- **Kong → Services:** HTTP reverse proxy over Render's private network
- **Progress → Auth:** HTTP call to `/internal/verify` to validate JWT tokens (cached in Redis for 120s)
- All services share a PostgreSQL instance but access **only their own tables**

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Services** | Python 3.12, FastAPI, SQLAlchemy 2.0, Uvicorn |
| **API Gateway** | Kong 3.9 (DB-less / declarative config) |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 (Render Key Value) |
| **Auth** | JWT (python-jose), bcrypt password hashing (passlib) |
| **Frontend** | Vanilla JS SPA, marked.js for Markdown rendering |
| **Containerization** | Docker, Docker Compose |
| **Deployment** | Render (Blueprint via `render.yaml`) |

---

## Quick Start (Docker)

### Prerequisites
- Docker + Docker Compose

### Run

```bash
cd /path/to/dsa
docker compose up --build
```

Wait for all services to start (≈30 seconds). The Kong gateway listens on **port 8080**
and proxies to the four FastAPI services. Then open:

> **http://localhost:8080**

Because the SPA is served as static files and the API base defaults to same-origin,
everything works on a single origin in local Docker. The first launch will automatically:
1. Create all database tables
2. Seed 12 DSA topics with 28 lessons
3. Seed 12 quizzes with 47+ questions

### Stop
```bash
docker compose down          # stop containers
docker compose down -v       # stop + delete database volume
```

> **Note:** In local Docker, Kong routes API requests but the SPA is served from the
> `frontend/` directory (open `frontend/index.html` directly or via a simple static server).
> The `docker compose` setup focuses on the API. To use the full SPA locally with Kong,
> serve `frontend/` with any static server and set `window.__API_BASE__` to
> `http://localhost:8080` in `frontend/config.js`.

---

## Deploying to Render

This repository includes a `render.yaml` Blueprint that declares **Kong** as the public
gateway plus the four FastAPI **private services**, a **static site** for the SPA,
a **Postgres** database, and a **Key Value (Redis)** instance. See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
for the complete step-by-step walkthrough. Summary:

1. **Push to GitHub** — commit and push the repo to a GitHub repository.
2. **Create a Render Blueprint** — in the Render Dashboard, create a new service from
   this repo; Render detects `render.yaml` and provisions all resources.
3. **Update `API_BASE_URL`** — after the first deploy, copy the `kong-gateway` public
   URL and set it as the `API_BASE_URL` env var on the `dsa-frontend` static site
   (replace the placeholder in `render.yaml` or set it in the Dashboard). Redeploy the
   frontend.
4. **Verify** — open the frontend URL; register a user, browse courses, take a quiz.

Key design decisions baked into the config:
- The microservices are **private** (no public URL) — only Kong is public.
- Kong's upstream hostnames are injected at runtime from Render's `fromService: hostport`
  (Render private hostnames carry a random suffix, so they can't be hardcoded).
- Each service honors the `PORT` env var so it works on Render without code changes.
- JWT secret is auto-generated; Postgres and Redis connection strings are wired via
  `fromDatabase` / `fromService`.

> ⚠️ **Important:** After the very first deploy you **must** update `API_BASE_URL` on the
> frontend static site to point at your real Kong URL — see the deployment guide.

---

## Running Locally (Without Docker)

### Prerequisites
- Python 3.12+
- PostgreSQL (or use the Docker postgres container)
- Redis (or use the Docker redis container)

### 1. Start infrastructure

```bash
docker compose up postgres redis -d

# Or install locally via Homebrew:
# brew install postgresql@16 redis
# brew services start postgresql@16
# brew services start redis
```

Create the database:
```bash
createdb dsalearning  # or: psql -c "CREATE DATABASE dsalearning;"
```

### 2. Start each Python service

```bash
cd auth-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://dsauser:dsapass@localhost:5432/dsalearning"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="dev-secret-change-me-in-production"
uvicorn main:app --port 4001 --reload
```

Repeat for `course-service` (:4002), `quiz-service` (:4003), `progress-service` (:4004).

> ⚠️ The course and quiz services auto-seed on first startup. You can also trigger re-seeding
> via `POST /courses/admin/seed` and `POST /quizzes/admin/seed`.

### 3. Start Kong (or use the old Node gateway)

Using Kong locally:
```bash
cd kong
docker build -t dsa-kong .
docker run -p 8080:8000 \
  -e AUTH_SERVICE_HOSTPORT=host.docker.internal:4001 \
  -e COURSE_SERVICE_HOSTPORT=host.docker.internal:4002 \
  -e QUIZ_SERVICE_HOSTPORT=host.docker.internal:4003 \
  -e PROGRESS_SERVICE_HOSTPORT=host.docker.internal:4004 \
  dsa-kong
```

### 4. Serve the frontend

```bash
cd frontend
# Set the API base to Kong's local port
echo 'window.__API_BASE__ = "http://localhost:8080";' > config.js
python3 -m http.server 3000
```

Open > **http://localhost:3000**

---

## API Documentation

All public API routes are served through Kong. Replace `http://localhost:8080` with
your Kong public URL in production.

### Auth Service

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Register a new user | ❌ |
| POST | `/auth/login` | Login and get JWT | ❌ |
| GET | `/auth/me` | Get current user | ✅ |
| POST | `/auth/logout` | Logout (blacklist token) | ✅ |
| GET | `/internal/verify?token=...` | Verify a token (internal) | ❌ |

### Course Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/courses/topics` | List all DSA topics |
| GET | `/courses/topics/{slug}` | Get a single topic |
| GET | `/courses/topics/{slug}/lessons` | List lessons in a topic |
| GET | `/courses/lessons/{slug}` | Get full lesson content (Markdown) |
| GET | `/courses/search?q=...` | Search topics & lessons |
| POST | `/courses/admin/seed` | Re-seed content |

### Quiz Service

| Method | Path | Description |
|--------|------|-------------|
| GET | `/quizzes` | List all quizzes |
| GET | `/quizzes/by-topic/{slug}` | Quizzes for a topic |
| GET | `/quizzes/{id}` | Get quiz with questions (no answers exposed) |
| POST | `/quizzes/{id}/submit` | Submit answers, get graded results |

### Progress Service (all routes require Bearer token)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/progress/lessons` | Mark lesson complete/incomplete |
| GET | `/progress/lessons` | Get user's lesson progress |
| POST | `/progress/quizzes` | Record a quiz attempt |
| GET | `/progress/quizzes` | Get user's quiz history |
| GET | `/progress/stats` | Get aggregate stats |
| GET | `/progress/leaderboard` | Get global leaderboard |

### Example: Full user flow via curl

```bash
# 1. Register
TOKEN=$(curl -s -X POST https://<kong-url>/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@ex.com","password":"secret123"}' | jq -r .access_token)

# 2. Browse topics
curl -s https://<kong-url>/courses/topics | jq

# 3. Read a lesson
curl -s https://<kong-url>/courses/lessons/arrays-intro | jq -r .content_md

# 4. Take a quiz
curl -s https://<kong-url>/quizzes/1 | jq '.questions[] | {id, prompt, options}'

# 5. Submit answers
curl -s -X POST https://<kong-url>/quizzes/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answers":[{"question_id":1,"selected_index":1},{"question_id":2,"selected_index":2}]}' | jq

# 6. Mark lesson complete
curl -s -X POST https://<kong-url>/progress/lessons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lesson_slug":"arrays-intro","completed":true}' | jq

# 7. View leaderboard
curl -s https://<kong-url>/progress/leaderboard | jq
```

---

## Project Structure

```
dsa/
├── render.yaml                 # Render Blueprint (Kong + services + DB + Redis)
├── docker-compose.yml          # Local Docker orchestration
├── DEPLOYMENT_GUIDE.md         # Step-by-step Render deployment guide
├── run_tests.py                # End-to-end smoke tests (31 tests)
├── .dockerignore
│
├── kong/                       # Kong API Gateway (DB-less)
│   ├── kong.yml                # Declarative config (template with __HOSTPORT__ placeholders)
│   ├── entrypoint.sh           # Renders kong.yml at startup from *_HOSTPORT env vars
│   └── Dockerfile              # Kong 3.9 image, renders config, proxy on :8000
│
├── frontend/                   # Frontend SPA (Render static site)
│   ├── index.html
│   ├── app.js                  # Routing, auth, all views
│   ├── config.js               # API base URL (set at deploy time via build.sh)
│   ├── style.css
│   └── build.sh                # Render build script — injects API_BASE_URL into config.js
│
├── auth-service/               # Authentication Service (FastAPI, private)
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── security.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── course-service/             # Course/Lesson Service (FastAPI, private)
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── seed.py                 # 12 topics, 28 lessons
│   ├── requirements.txt
│   └── Dockerfile
│
├── quiz-service/               # Quiz Service (FastAPI, private)
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── seed.py                 # 12 quizzes, 47+ questions
│   ├── requirements.txt
│   └── Dockerfile
│
├── progress-service/           # Progress Tracking Service (FastAPI, private)
│   ├── main.py
│   ├── config.py               # Normalizes AUTH_SERVICE_URL scheme
│   ├── models.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── gateway-old/                # Deprecated Node.js gateway (kept for reference)
│   └── ...
│
└── shared/
    └── constants.py            # Shared constants (no secrets)
```

---

## DSA Content

The platform includes **12 topics** with **28 lessons** and **12 quizzes** (47+ questions), all with genuine educational content:

| Topic | Difficulty | Lessons | Quiz Questions |
|-------|-----------|---------|----------------|
| 📊 Arrays & Dynamic Arrays | Beginner | 4 | 5 |
| 🔗 Linked Lists | Beginner | 3 | 5 |
| 📚 Stacks & Queues | Beginner | 2 | 4 |
| 🌳 Trees & Binary Search Trees | Intermediate | 3 | 5 |
| ⛰️ Heaps & Priority Queues | Intermediate | 2 | 4 |
| #️⃣ Hash Tables & Hashing | Beginner | 1 | 4 |
| 🕸️ Graphs | Intermediate | 3 | 5 |
| 🌀 Recursion & Backtracking | Intermediate | 2 | 4 |
| 🔍 Sorting & Searching | Beginner | 2 | 5 |
| 🧩 Dynamic Programming | Advanced | 3 | 5 |
| 🪙 Greedy Algorithms | Intermediate | 1 | 4 |
| 🗺️ Advanced Graph Algorithms | Advanced | 2 | 4 |

Each lesson includes clear explanations with intuition and trade-offs, Python code examples
with syntax highlighting, complexity tables (time/space), "Why it works" explanations,
real-world applications, and interview tips. Each quiz question includes a detailed
explanation shown after submission.

---

## Testing

The project includes a comprehensive end-to-end test suite that validates all services
without requiring Docker, PostgreSQL, or Redis (uses SQLite + fake Redis):

```bash
cd /path/to/dsa

# Create a Python 3.12+ venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r auth-service/requirements.txt

# Run all tests
python run_tests.py
```

**Test coverage (31 tests):**

- **Auth Service (7 tests):** register, login, duplicate rejection, wrong password, token validation, internal verify
- **Course Service (9 tests):** topic listing, topic detail, lesson listing, lesson content, search, 404 handling
- **Quiz Service (8 tests):** quiz listing, by-topic filter, quiz detail, correct-answer hiding, submission, scoring
- **Progress Service (7 tests):** lesson completion, progress retrieval, quiz attempt recording, stats, leaderboard

---

## Features

### For Students
- **Dark-themed, responsive UI** — works on desktop and mobile
- **Markdown-rendered lessons** with syntax-highlighted code blocks
- **Interactive quizzes** with immediate feedback and explanations
- **Progress dashboard** — lessons completed, quiz history, average score
- **Leaderboard** — compete with other students
- **Search** — find topics and lessons by keyword

### Architecture Highlights
- **Kong API gateway** — single public entry point, declarative config, CORS plugin
- **Service isolation** — each service owns its tables and can be deployed independently
- **Private services on Render** — microservices are not exposed to the internet
- **JWT auth** with token blacklisting for logout
- **Redis caching** — course content and auth verification cached with TTL
- **Environment-driven config** — Kong upstreams and service URLs resolve at runtime
- **Auto-seeding** — database populates on first startup
- **Health checks** — every service exposes `/health`

---

## Environment Variables

| Variable | Default (local) | Used by |
|----------|-----------------|---------|
| `DATABASE_URL` | `postgresql://dsauser:dsapass@localhost:5432/dsalearning` | All Python services |
| `REDIS_URL` | `redis://localhost:6379` | All Python services |
| `JWT_SECRET` | `dev-secret-change-me-in-production` | Auth Service |
| `AUTH_SERVICE_URL` | `http://auth-service:4001` | Progress Service |
| `AUTH_SERVICE_HOSTPORT` | `auth-service:4001` | Kong (entrypoint.sh) |
| `COURSE_SERVICE_HOSTPORT` | `course-service:4002` | Kong (entrypoint.sh) |
| `QUIZ_SERVICE_HOSTPORT` | `quiz-service:4003` | Kong (entrypoint.sh) |
| `PROGRESS_SERVICE_HOSTPORT` | `progress-service:4004` | Kong (entrypoint.sh) |
| `PORT` | `4001`/`4002`/`4003`/`4004` | All services (Render sets this) |
| `API_BASE_URL` | _(empty = same-origin)_ | Frontend (build.sh → config.js) |

### On Render, these are wired automatically by `render.yaml`:
- `DATABASE_URL` ← `fromDatabase: dsa-postgres.connectionString`
- `REDIS_URL` ← `fromService: dsa-redis.connectionString`
- `JWT_SECRET` ← `generateValue: true`
- `AUTH_SERVICE_URL` ← `fromService: auth-service.hostport` (scheme added by config.py)
- `*_HOSTPORT` (Kong) ← `fromService: <service>.hostport`
- `API_BASE_URL` ← set to your Kong public URL (update after first deploy)

> ⚠️ **Production warning:** Never use the default `JWT_SECRET` in production. On Render it
> is auto-generated; locally, set a strong value in your environment.

---

## License

MIT — This is a demo/educational project. Use freely.
