const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require("path");

const PORT = process.env.PORT || 8080;

const AUTH_URL = process.env.AUTH_SERVICE_URL || "http://localhost:4001";
const COURSE_URL = process.env.COURSE_SERVICE_URL || "http://localhost:4002";
const QUIZ_URL = process.env.QUIZ_SERVICE_URL || "http://localhost:4003";
const PROGRESS_URL = process.env.PROGRESS_SERVICE_URL || "http://localhost:4004";

const app = express();

app.use(express.json());

// ---- Health ----
app.get("/health", (_req, res) => {
  res.json({ service: "gateway", status: "ok" });
});

// ---- Service proxies ----
// Each upstream keeps its own path prefix; the gateway just forwards.

const commonProxyOptions = (target, name) => ({
  target,
  changeOrigin: true,
  logLevel: "warn",
  onError: (err, _req, res) => {
    console.error(`[${name}] proxy error:`, err.message);
    if (!res.headersSent) {
      res.status(502).json({ error: `${name} unavailable`, detail: err.message });
    }
  },
});

// Auth Service -> /auth/*  and  /internal/*
app.use(["/auth", "/internal"], createProxyMiddleware({
  ...commonProxyOptions(AUTH_URL, "auth"),
  pathRewrite: { "^/auth": "/auth" },
}));

// Course Service -> /courses/*
app.use("/courses", createProxyMiddleware({
  ...commonProxyOptions(COURSE_URL, "course"),
}));

// Quiz Service -> /quizzes/*
app.use("/quizzes", createProxyMiddleware({
  ...commonProxyOptions(QUIZ_URL, "quiz"),
}));

// Progress Service -> /progress/*
app.use("/progress", createProxyMiddleware({
  ...commonProxyOptions(PROGRESS_URL, "progress"),
}));

// ---- Static UI ----
app.use(express.static(path.join(__dirname, "public")));

// SPA fallback: any non-API GET serves index.html
app.get(/^\/(?!auth|internal|courses|quizzes|progress|health).*/, (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`DSA Learning Platform Gateway listening on :${PORT}`);
  console.log(`  Auth     -> ${AUTH_URL}`);
  console.log(`  Course   -> ${COURSE_URL}`);
  console.log(`  Quiz     -> ${QUIZ_URL}`);
  console.log(`  Progress -> ${PROGRESS_URL}`);
});
