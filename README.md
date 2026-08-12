# 🧠 DSAHub — Microservice-Based DSA Learning Platform

A fully functional, production-architected learning platform for **Data Structures & Algorithms**, built as a microservices application. Students can register, browse 12 DSA topics with 28 in-depth lessons, take quizzes, track progress, and compete on a leaderboard.

![Architecture](https://img.shields.io/badge/architecture-microservices-blue) ![Status](https://img.shields.io/badge/tests-31%2F31%20passing-brightgreen)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start (Docker)](#quick-start-docker)
- [Running Locally (Without Docker)](#running-locally-without-docker)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [DSA Content](#dsa-content)
- [Testing](#testing)
- [Screenshots / Features](#features)

---

## Overview

DSAHub is designed to demonstrate a real microservices architecture while providing genuine educational value. Each service is independently deployable, has its own database tables, and communicates through the API gateway.

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
                    ┌──────────────────────────────────┐
                    │         Web UI (SPA)              │
                    │   HTML/CSS/JS (served by gateway) │
                    └──────────────┬───────────────────┘
                                   │ HTTP
                    ┌──────────────▼───────────────────┐
                    │       API Gateway (:8080)         │
                    │   Node.js + Express + Proxy       │
                    │   Routes /auth /courses /quizzes  │
                    │   /progress + serves static UI    │
                    └──┬──────┬──────┬──────┬───────────┘
                       │      │      │      │
              ┌────────▼┐ ┌───▼───┐ ┌▼─────┐ ┌▼──────────┐
              │  Auth   │ │Course │ │ Quiz │ │ Progress  │
              │ Service │ │Service│ │Service│ │  Service  │
              │  :4001  │ │ :4002 │ │ :4003│ │  :4004    │
              │ FastAPI │ │FastAPI│ │FastAPI│ │  FastAPI  │
              └────┬────┘ └───┬───┘ └──┬───┘ └────┬──────┘
                   │          │        │          │
              ┌────┴──────────┴────────┴──────────┴────┐
              │     PostgreSQL (:5432)                  │
              │     Shared DB, per-service tables       │
              └─────────────────────────────────────────┘
              ┌────┴──────────┴────────┴──────────┴────┐
              │     Redis (:6379)                       │
              │     Caching + token blacklist           │
              └─────────────────────────────────────────┘
```

### Service Responsibilities

| Service | Port | Responsibility |
|---------|------|---------------|
| **Gateway** | 8080 | Reverse proxy, static UI hosting, request routing |
| **Auth Service** | 4001 | User registration, login, JWT issuance, token verification |
| **Course Service** | 4002 | DSA topics, lessons, content delivery, search |
| **Quiz Service** | 4003 | Quiz questions, answer submission, auto-grading |
| **Progress Service** | 4004 | Lesson completion tracking, quiz score recording, leaderboard |
| **PostgreSQL** | 5432 | Shared database (each service owns its own tables) |
| **Redis** | 6379 | Response caching, auth token blacklist, token verification cache |

### Inter-Service Communication
- **Gateway → Services:** HTTP reverse proxy (http-proxy-middleware)
- **Progress → Auth:** HTTP call to verify JWT tokens (cached in Redis for 120s)
- All services share a PostgreSQL instance but access **only their own tables**

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Services** | Python 3.12, FastAPI, SQLAlchemy 2.0, Uvicorn |
| **API Gateway** | Node.js 20, Express, http-proxy-middleware |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Auth** | JWT (python-jose), bcrypt password hashing (passlib) |
| **Frontend** | Vanilla JS SPA, marked.js for Markdown rendering |
| **Containerization** | Docker, Docker Compose |

---

## Quick Start (Docker)

### Prerequisites
- Docker + Docker Compose

### Run

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
docker compose up --build
```

Wait for all services to start (≈30 seconds). Then open:

> **http://localhost:8080**

The first launch will automatically:
1. Create all database tables
2. Seed 12 DSA topics with 28 lessons
3. Seed 12 quizzes with 47+ questions

### Stop
```bash
docker compose down          # stop containers
docker compose down -v       # stop + delete database volume
```

---

## Running Locally (Without Docker)

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL (or use the Docker postgres container)
- Redis (or use the Docker redis container)

### 1. Start infrastructure

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa
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
uvicorn main:app --port 4001 --reload
```

Repeat for `course-service` (:4002), `quiz-service` (:4003), `progress-service` (:4004).

> ⚠️ The course and quiz services auto-seed on first startup. You can also trigger re-seeding via `POST /courses/admin/seed` and `POST /quizzes/admin/seed`.

### 3. Start the gateway

```bash
cd gateway
npm install
export AUTH_SERVICE_URL=http://localhost:4001
export COURSE_SERVICE_URL=http://localhost:4002
export QUIZ_SERVICE_URL=http://localhost:4003
export PROGRESS_SERVICE_URL=http://localhost:4004
npm start
```

Open > **http://localhost:8080**

---

## API Documentation

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
TOKEN=$(curl -s -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@ex.com","password":"secret123"}' | jq -r .access_token)

# 2. Browse topics
curl -s http://localhost:8080/courses/topics | jq

# 3. Read a lesson
curl -s http://localhost:8080/courses/lessons/arrays-intro | jq -r .content_md

# 4. Take a quiz
curl -s http://localhost:8080/quizzes/1 | jq '.questions[] | {id, prompt, options}'

# 5. Submit answers
curl -s -X POST http://localhost:8080/quizzes/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answers":[{"question_id":1,"selected_index":1},{"question_id":2,"selected_index":2}]}' | jq

# 6. Mark lesson complete
curl -s -X POST http://localhost:8080/progress/lessons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lesson_slug":"arrays-intro","completed":true}' | jq

# 7. View leaderboard
curl -s http://localhost:8080/progress/leaderboard | jq
```

---

## Project Structure

```
dsa/                              ← /Users/saibhargav/Documents/MyProjects/dsa
├── docker-compose.yml           # Orchestrates all services
├── run_tests.py                 # End-to-end smoke tests (31 tests)
├── .dockerignore
│
├── gateway/                     # API Gateway (Node.js/Express)
│   ├── server.js                # Proxy routes + static UI serving
│   ├── package.json
│   ├── Dockerfile
│   └── public/                  # Frontend SPA
│       ├── index.html
│       ├── style.css
│       └── app.js               # Routing, auth, all views
│
├── auth-service/                # Authentication Service (FastAPI)
│   ├── main.py                  # Register/login/logout/verify endpoints
│   ├── config.py                # DB + settings
│   ├── models.py                # User model
│   ├── security.py              # JWT + bcrypt
│   ├── seed.py                  # (no seed needed)
│   ├── requirements.txt
│   └── Dockerfile
│
├── course-service/              # Course/Lesson Service (FastAPI)
│   ├── main.py                  # Topics, lessons, search endpoints
│   ├── config.py
│   ├── models.py                # Topic + Lesson models
│   ├── seed.py                  # 📚 12 topics, 28 lessons (rich Markdown)
│   ├── requirements.txt
│   └── Dockerfile
│
├── quiz-service/                # Quiz Service (FastAPI)
│   ├── main.py                  # Quiz listing, submission, grading
│   ├── config.py
│   ├── models.py                # Quiz + Question models
│   ├── seed.py                  # 📝 12 quizzes, 47+ questions
│   ├── requirements.txt
│   └── Dockerfile
│
├── progress-service/            # Progress Tracking Service (FastAPI)
│   ├── main.py                  # Lesson progress, quiz attempts, leaderboard
│   ├── config.py
│   ├── models.py                # LessonProgress + QuizAttempt models
│   ├── requirements.txt
│   └── Dockerfile
│
└── shared/
    └── constants.py             # Shared constants
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

Each lesson includes:
- Clear explanations with **intuition and trade-offs**
- **Python code examples** with syntax highlighting
- **Complexity tables** (time/space)
- **"Why it works" explanations**
- **Real-world applications**
- **Interview tips**

Each quiz question includes a **detailed explanation** shown after submission.

---

## Testing

The project includes a comprehensive end-to-end test suite that validates all services without requiring Docker, PostgreSQL, or Redis (uses SQLite + fake Redis):

```bash
cd /Users/saibhargav/Documents/MyProjects/dsa

# Create a Python 3.12+ venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r auth-service/requirements.txt

# Run all tests
python run_tests.py
```

**Test coverage (31 tests):**

- **Auth Service (7 tests):** register, login, duplicate rejection, wrong password, token validation, internal verify
- **Course Service (9 tests):** topic listing, topic detail, lesson listing, lesson content (Markdown + code blocks), search, 404 handling, content richness
- **Quiz Service (8 tests):** quiz listing, by-topic filter, quiz detail, correct-answer hiding, submission, scoring, per-question details, explanations
- **Progress Service (7 tests):** lesson completion, progress retrieval, quiz attempt recording, attempt history, stats, leaderboard, unauthenticated rejection

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
- **Service isolation** — each service owns its tables and can be deployed independently
- **JWT auth** with token blacklisting for logout
- **Redis caching** — course content and auth verification cached with TTL
- **API Gateway pattern** — single entry point, clean routing, static UI hosting
- **Auto-seeding** — database populates on first startup
- **Health checks** — every service exposes `/health`
- **Docker Compose** — one command to run the entire system

---

## Environment Variables

| Variable | Default | Used by |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://dsauser:dsapass@postgres:5432/dsalearning` | All Python services |
| `REDIS_URL` | `redis://redis:6379` | All Python services |
| `JWT_SECRET` | `dev-secret-change-me-in-production` | Auth Service |
| `AUTH_SERVICE_URL` | `http://auth-service:4001` | Progress Service, Gateway |
| `COURSE_SERVICE_URL` | `http://course-service:4002` | Gateway |
| `QUIZ_SERVICE_URL` | `http://quiz-service:4003` | Gateway |
| `PROGRESS_SERVICE_URL` | `http://progress-service:4004` | Gateway |
| `PORT` | varies per service | All services |

> ⚠️ **Production warning:** Change `JWT_SECRET` and database credentials before deploying.

---

## Deploying to Render with Kong

This repository includes a `render.yaml` that declares the Kong gateway plus the Python microservices. The microservices are configured as internal services and Kong is the single public gateway.

Steps to deploy:

1. Push this repository to GitHub (or a Git provider Render can access):

```bash
git add .
git commit -m "Add Render deployment config and Kong gateway"
git push origin main
```

2. On Render.com, create a new service and connect this repository. Render will detect `render.yaml` and create the listed services automatically. Ensure the `kong-gateway` service is public (default) and the other services are internal.

3. If Kong doesn't pick up the declarative config automatically, set the environment variable `KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml` on the `kong-gateway` service (the `render.yaml` already includes this).

4. Visit the Kong public URL (the `kong-gateway` service) — that is the API entrypoint for the SPA and API routes (e.g. `/auth`, `/courses`, `/quizzes`, `/progress`).

Notes:
- Render provides internal DNS between services in the same team — the service names used in `kong/kong.yml` match the service names in `render.yaml`.
- Monitor service logs on Render to confirm successful startup and that Kong is routing requests to the internal services.


## License

MIT — This is a demo/educational project. Use freely.
