/* ============================================================
   DSA Learning Platform — Frontend SPA
   ============================================================ */

const API = window.__API_BASE__ || "http://localhost:8080";
const TOKEN_KEY = "dsa_token";
const USER_KEY = "dsa_user";

// ---------- State ----------
let state = {
  user: null,
  topics: [],
  currentTopic: null,
  currentLessonSlug: null,
  currentQuiz: null,
  quizAnswers: {},
  completedLessons: new Set(),
};

// ---------- Helpers ----------
function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  state.user = user;
}
function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  state.user = null;
}
function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
}

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: { ...authHeaders(), ...(opts.headers || {}) },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, detail: data.detail || data.error || "Request failed" };
  return data;
}

function toast(msg, type = "success") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function render(html) {
  document.getElementById("app").innerHTML = html;
}

function setActiveNav(route) {
  document.querySelectorAll(".nav-links a").forEach(a => {
    a.classList.toggle("active", a.dataset.route === route);
  });
}

// ---------- Router ----------
function navigate(route, params = {}) {
  switch (route) {
    case "home": renderHome(); break;
    case "catalog": renderCatalog(); break;
    case "topic": renderTopic(params.slug); break;
    case "lesson": renderLesson(params.slug); break;
    case "quiz": renderQuiz(params.id); break;
    case "dashboard": renderDashboard(); break;
    case "leaderboard": renderLeaderboard(); break;
    case "login": renderAuth("login"); break;
    case "register": renderAuth("register"); break;
    default: renderHome();
  }
  window.scrollTo(0, 0);
}

// ---------- Nav auth area ----------
function renderNavAuth() {
  const el = document.getElementById("navAuth");
  if (state.user) {
    el.innerHTML = `
      <span style="color:var(--text-dim);font-size:.9rem">Hi, ${state.user.name}</span>
      <button class="btn btn-ghost btn-sm" onclick="doLogout()">Logout</button>`;
  } else {
    el.innerHTML = `
      <button class="btn btn-ghost btn-sm" onclick="navigate('login')">Login</button>
      <button class="btn btn-primary btn-sm" onclick="navigate('register')">Sign Up</button>`;
  }
}

async function doLogout() {
  try { await api("/auth/logout", { method: "POST" }); } catch (e) {}
  clearAuth();
  renderNavAuth();
  navigate("home");
  toast("Logged out");
}

function requireAuth() {
  if (!state.user) {
    toast("Please log in first", "error");
    navigate("login");
    return false;
  }
  return true;
}

// ---------- Views ----------
async function renderHome() {
  setActiveNav("home");
  try {
    state.topics = await api("/courses/topics");
  } catch (e) {
    state.topics = [];
  }
  const totalLessons = state.topics.reduce((s, t) => s + t.lesson_count, 0);
  render(`
    <section class="hero">
      <h1>Master <span class="accent">Data Structures</span> & Algorithms</h1>
      <p>Learn DSA through structured topics, hands-on lessons, and quizzes. Track your progress and compete on the leaderboard.</p>
      <div style="display:flex;gap:12px;justify-content:center">
        <button class="btn btn-primary" onclick="navigate('catalog')">Browse Courses</button>
        ${state.user ? `<button class="btn btn-ghost" onclick="navigate('dashboard')">My Progress</button>`
                     : `<button class="btn btn-ghost" onclick="navigate('register')">Get Started Free</button>`}
      </div>
      <div class="hero-stats">
        <div class="hero-stat"><div class="num">${state.topics.length}</div><div class="label">Topics</div></div>
        <div class="hero-stat"><div class="num">${totalLessons}</div><div class="label">Lessons</div></div>
        <div class="hero-stat"><div class="num">${state.topics.length}</div><div class="label">Quizzes</div></div>
      </div>
    </section>
    <h2 style="text-align:center;margin-top:40px;margin-bottom:0">Explore Topics</h2>
    <div class="topic-grid">
      ${state.topics.slice(0, 6).map(topicCard).join("")}
    </div>
    ${state.topics.length > 6 ? `<p style="text-align:center;margin-top:24px"><a class="back-link" onclick="navigate('catalog')">View all ${state.topics.length} topics →</a></p>` : ""}
  `);
}

function topicCard(t) {
  const diffClass = (t.difficulty || "Beginner").toLowerCase();
  return `
    <div class="topic-card" onclick="navigate('topic',{slug:'${t.slug}'})">
      <div class="icon">${t.icon || "📘"}</div>
      <h3>${t.title}</h3>
      <p>${t.description}</p>
      <div class="meta">
        <span class="badge badge-${diffClass}">${t.difficulty}</span>
        <span>📖 ${t.lesson_count} lessons</span>
      </div>
    </div>`;
}

async function renderCatalog() {
  setActiveNav("catalog");
  render(`<div class="section-head"><h2>All Courses</h2></div>
          <input class="search-box" id="searchInput" placeholder="Search topics & lessons..." oninput="doSearch()" />
          <div id="topicGrid" class="topic-grid"><div class="spinner">Loading…</div></div>
          <div id="searchResults" class="search-results"></div>`);
  try {
    state.topics = await api("/courses/topics");
    document.getElementById("topicGrid").innerHTML = state.topics.map(topicCard).join("");
  } catch (e) {
    document.getElementById("topicGrid").innerHTML = `<div class="empty-state"><div class="icon">⚠️</div><p>Could not load courses. Is the course service running?</p></div>`;
  }
}

let searchTimer;
async function doSearch() {
  const q = document.getElementById("searchInput").value.trim();
  const grid = document.getElementById("topicGrid");
  const results = document.getElementById("searchResults");
  if (!q) { grid.style.display = "grid"; results.innerHTML = ""; return; }
  grid.style.display = "none";
  clearTimeout(searchTimer);
  searchTimer = setTimeout(async () => {
    try {
      const data = await api(`/courses/search?q=${encodeURIComponent(q)}`);
      results.innerHTML = `
        ${data.topics.length ? `<h4 style="margin:12px 0 8px;color:var(--text-dim)">Topics</h4>` : ""}
        ${data.topics.map(t => `<div class="search-result-item" onclick="navigate('topic',{slug:'${t.slug}'})"><span style="font-size:1.3rem">${t.icon||"📘"}</span> ${t.title}</div>`).join("")}
        ${data.lessons.length ? `<h4 style="margin:16px 0 8px;color:var(--text-dim)">Lessons</h4>` : ""}
        ${data.lessons.map(l => `<div class="search-result-item" onclick="navigate('lesson',{slug:'${l.slug}'})">📖 ${l.title} <span style="color:var(--text-dim);font-size:.85rem">— ${l.topic_slug}</span></div>`).join("")}
        ${!data.topics.length && !data.lessons.length ? `<p style="color:var(--text-dim);padding:16px">No results for "${q}"</p>` : ""}
      `;
    } catch (e) { results.innerHTML = "<p style='color:var(--text-dim)'>Search failed.</p>"; }
  }, 250);
}

async function renderTopic(slug) {
  setActiveNav("catalog");
  render(`<div class="spinner">Loading topic…</div>`);
  try {
    const [topic, lessons] = await Promise.all([
      api(`/courses/topics/${slug}`),
      api(`/courses/topics/${slug}/lessons`),
    ]);
    const quizzes = await api(`/quizzes/by-topic/${slug}`).catch(() => []);
    render(`
      <div class="section-head">
        <div><span class="back-link" onclick="navigate('catalog')">← All Courses</span>
        <h2 style="margin-top:8px">${topic.icon||"📘"} ${topic.title}</h2></div>
        <span class="badge badge-${(topic.difficulty||'beginner').toLowerCase()}">${topic.difficulty}</span>
      </div>
      <p style="color:var(--text-dim);margin-bottom:24px">${topic.description}</p>
      <h3>Lessons (${lessons.length})</h3>
      <div class="topic-grid" style="grid-template-columns:1fr">
        ${lessons.map(l => {
          const done = state.completedLessons.has(l.slug);
          return `<div class="topic-card" onclick="navigate('lesson',{slug:'${l.slug}'})">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div><h3 style="margin-bottom:4px">${done ? '<span class="check" style="color:var(--accent-2)">✓</span> ' : ''}${l.title}</h3>
              <p style="margin:0">${l.summary}</p></div>
              <span style="color:var(--text-dim);font-size:.85rem;white-space:nowrap">⏱ ${l.duration_minutes} min</span>
            </div>
          </div>`;
        }).join("")}
      </div>
      ${quizzes.length ? `
        <h3 style="margin-top:32px">Quiz</h3>
        ${quizzes.map(qz => `<div class="topic-card" style="cursor:pointer" onclick="navigate('quiz',{id:${qz.id}})">
          <h3 style="margin-bottom:4px">📝 ${qz.title}</h3>
          <p style="margin:0">${qz.description||''}</p>
          <p style="margin:8px 0 0;color:var(--text-dim);font-size:.85rem">${qz.question_count} questions</p>
        </div>`).join("")}` : ""}
    `);
  } catch (e) {
    render(`<div class="empty-state"><div class="icon">⚠️</div><p>Topic not found.</p><p><a class="back-link" onclick="navigate('catalog')">← Back to courses</a></p></div>`);
  }
}

async function renderLesson(slug) {
  setActiveNav("catalog");
  render(`<div class="spinner">Loading lesson…</div>`);
  try {
    const lesson = await api(`/courses/lessons/${slug}`);
    const lessons = await api(`/courses/topics/${lesson.topic_slug}/lessons`);
    state.currentLessonSlug = slug;
    const idx = lessons.findIndex(l => l.slug === slug);
    const prev = idx > 0 ? lessons[idx - 1] : null;
    const next = idx < lessons.length - 1 ? lessons[idx + 1] : null;
    const done = state.completedLessons.has(slug);

    const contentHtml = marked.parse(lesson.content_md);

    render(`
      <div class="section-head">
        <span class="back-link" onclick="navigate('topic',{slug:'${lesson.topic_slug}'})">← ${lesson.topic_title}</span>
      </div>
      <div class="lesson-layout">
        <aside class="lesson-sidebar">
          <h4>${lesson.topic_title}</h4>
          ${lessons.map(l => {
            const lDone = state.completedLessons.has(l.slug);
            return `<div class="lesson-item ${l.slug===slug?'active':''}" onclick="navigate('lesson',{slug:'${l.slug}'})">
              ${lDone ? '<span class="check">✓</span>' : '<span style="opacity:.4">○</span>'}
              <span>${l.title}</span>
            </div>`;
          }).join("")}
        </aside>
        <div class="lesson-content">
          <h1>${lesson.title}</h1>
          <p class="lesson-summary">${lesson.summary}</p>
          <div class="lesson-body">${contentHtml}</div>
          <div class="lesson-actions">
            <button class="btn ${done ? 'btn-ghost' : 'btn-primary'}" onclick="toggleComplete('${slug}')">
              ${done ? '✓ Completed' : 'Mark as Complete'}
            </button>
            <span style="color:var(--text-dim);font-size:.85rem">⏱ ${lesson.duration_minutes} min</span>
            <div style="margin-left:auto;display:flex;gap:8px">
              ${prev ? `<button class="btn btn-ghost btn-sm" onclick="navigate('lesson',{slug:'${prev.slug}'})">← ${prev.title}</button>` : ""}
              ${next ? `<button class="btn btn-ghost btn-sm" onclick="navigate('lesson',{slug:'${next.slug}'})">${next.title} →</button>` : ""}
            </div>
          </div>
        </div>
      </div>
    `);
  } catch (e) {
    render(`<div class="empty-state"><div class="icon">⚠️</div><p>Lesson not found.</p></div>`);
  }
}

async function toggleComplete(slug) {
  if (!requireAuth()) return;
  const done = state.completedLessons.has(slug);
  try {
    await api("/progress/lessons", {
      method: "POST",
      body: JSON.stringify({ lesson_slug: slug, completed: !done }),
    });
    if (done) state.completedLessons.delete(slug);
    else state.completedLessons.add(slug);
    toast(!done ? "Lesson completed! 🎉" : "Marked as incomplete");
    renderLesson(slug);
  } catch (e) {
    toast(e.detail || "Failed to save progress", "error");
  }
}

async function renderQuiz(id) {
  setActiveNav("catalog");
  if (!requireAuth()) return;
  render(`<div class="spinner">Loading quiz…</div>`);
  try {
    const quiz = await api(`/quizzes/${id}`);
    state.currentQuiz = quiz;
    state.quizAnswers = {};
    render(`
      <div class="section-head">
        <span class="back-link" onclick="navigate('topic',{slug:'${quiz.topic_slug}'})">← Back</span>
      </div>
      <div class="quiz-card">
        <h2>📝 ${quiz.title}</h2>
        <p style="color:var(--text-dim);margin:8px 0 4px">${quiz.description||''}</p>
        <p style="color:var(--text-dim);font-size:.85rem;margin-bottom:24px">${quiz.question_count} questions</p>
        <form id="quizForm" onsubmit="submitQuiz(event,${id})">
          ${quiz.questions.map((q, qi) => `
            <div class="quiz-question">
              <div class="q-text">${qi+1}. ${q.prompt}</div>
              ${q.options.map((opt, oi) => `
                <label class="quiz-option" onclick="selectOption(this,${q.id})">
                  <input type="radio" name="q${q.id}" value="${oi}" onchange="recordAnswer(${q.id},${oi})" />
                  <span>${opt}</span>
                </label>`).join("")}
            </div>`).join("")}
          <button type="submit" class="btn btn-primary" style="margin-top:8px">Submit Quiz</button>
        </form>
      </div>
    `);
  } catch (e) {
    render(`<div class="empty-state"><div class="icon">⚠️</div><p>Quiz not found.</p></div>`);
  }
}

function selectOption(labelEl, qid) {
  document.querySelectorAll(`input[name="q${qid}"]`).forEach(r => {
    r.closest('.quiz-option').classList.remove('selected');
  });
  labelEl.classList.add('selected');
  labelEl.querySelector('input').checked = true;
  recordAnswer(qid, parseInt(labelEl.querySelector('input').value));
}

function recordAnswer(qid, idx) {
  state.quizAnswers[qid] = idx;
}

async function submitQuiz(e, id) {
  e.preventDefault();
  const quiz = state.currentQuiz;
  const answered = Object.keys(state.quizAnswers).length;
  if (answered < quiz.question_count) {
    if (!confirm(`You've answered ${answered} of ${quiz.question_count} questions. Submit anyway?`)) return;
  }
  const answers = quiz.questions.map(q => ({
    question_id: q.id,
    selected_index: state.quizAnswers[q.id] ?? -1,
  }));
  try {
    const result = await api(`/quizzes/${id}/submit`, {
      method: "POST", body: JSON.stringify({ answers }),
    });
    // Record to progress service
    try {
      await api("/progress/quizzes", {
        method: "POST",
        body: JSON.stringify({
          quiz_id: id, topic_slug: quiz.topic_slug,
          score: result.score, correct: result.correct, total: result.total,
        }),
      });
    } catch (e) { /* progress save optional */ }

    const pct = result.score;
    const color = pct >= 80 ? 'var(--accent-2)' : pct >= 50 ? 'var(--warn)' : 'var(--danger)';
    render(`
      <div class="section-head"><span class="back-link" onclick="navigate('topic',{slug:'${quiz.topic_slug}'})">← Back</span></div>
      <div class="quiz-result">
        <div class="score-display">
          <div class="score-num" style="color:${color}">${pct}%</div>
          <div class="score-label">${result.correct} / ${result.total} correct</div>
        </div>
        <h3 style="margin:24px 0 16px">Review</h3>
        ${result.details.map((d, i) => `
          <div class="result-item ${d.is_correct?'correct':'wrong'}">
            <div class="q">${i+1}. ${d.prompt}</div>
            ${d.selected_index >= 0 ? `<div class="ans">Your answer: <strong style="color:${d.is_correct?'var(--accent-2)':'var(--danger)'}">${quiz.questions[i].options[d.selected_index]}</strong></div>` : `<div class="ans">Your answer: <em>(skipped)</em></div>`}
            <div class="ans">Correct answer: <strong style="color:var(--accent-2)">${quiz.questions[i].options[d.correct_index]}</strong></div>
            ${d.explanation ? `<div class="expl">💡 ${d.explanation}</div>` : ""}
          </div>`).join("")}
        <div style="margin-top:24px;display:flex;gap:12px">
          <button class="btn btn-primary" onclick="navigate('quiz',{id:${id}})">Retry Quiz</button>
          <button class="btn btn-ghost" onclick="navigate('topic',{slug:'${quiz.topic_slug}'})">Back to Topic</button>
          <button class="btn btn-ghost" onclick="navigate('dashboard')">View Progress</button>
        </div>
      </div>
    `);
    toast(`Quiz submitted: ${pct}%`, pct >= 50 ? "success" : "error");
  } catch (e) {
    toast(e.detail || "Failed to submit quiz", "error");
  }
}

async function renderDashboard() {
  setActiveNav("dashboard");
  if (!requireAuth()) return;
  render(`<div class="spinner">Loading your progress…</div>`);
  try {
    const [stats, lessons, attempts] = await Promise.all([
      api("/progress/stats").catch(() => null),
      api("/progress/lessons").catch(() => ({ completed_lessons: [] })),
      api("/progress/quizzes").catch(() => ({ attempts: [] })),
    ]);
    state.completedLessons = new Set(lessons.completed_lessons || []);

    render(`
      <div class="section-head"><h2>My Progress</h2></div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-val">${stats?.lessons_completed ?? 0}</div><div class="stat-lbl">Lessons Completed</div></div>
        <div class="stat-card"><div class="stat-val">${stats?.quizzes_taken ?? 0}</div><div class="stat-lbl">Quizzes Taken</div></div>
        <div class="stat-card"><div class="stat-val">${stats?.best_avg_score ?? 0}%</div><div class="stat-lbl">Avg Score</div></div>
      </div>
      <h3>Recent Quiz Attempts</h3>
      ${(attempts.attempts||[]).length ? `
        <table class="lb-table">
          <tr><th>Topic</th><th>Score</th><th>Result</th><th>Date</th></tr>
          ${attempts.attempts.slice(0,10).map(a => `
            <tr>
              <td>${a.topic_slug}</td>
              <td><strong style="color:${a.score>=80?'var(--accent-2)':a.score>=50?'var(--warn)':'var(--danger)'}">${a.score}%</strong></td>
              <td>${a.correct}/${a.total}</td>
              <td style="color:var(--text-dim)">${a.created_at ? new Date(a.created_at).toLocaleDateString() : ''}</td>
            </tr>`).join("")}
        </table>` : `<div class="empty-state"><div class="icon">📝</div><p>No quizzes taken yet. <a class="back-link" onclick="navigate('catalog')">Take a quiz →</a></p></div>`}
      <h3 style="margin-top:32px">Completed Lessons</h3>
      ${(lessons.completed_lessons||[]).length ? `
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px">
          ${lessons.completed_lessons.map(s => `<span class="badge badge-beginner">✓ ${s}</span>`).join("")}
        </div>` : `<div class="empty-state"><div class="icon">📖</div><p>No lessons completed yet. <a class="back-link" onclick="navigate('catalog')">Start learning →</a></p></div>`}
    `);
  } catch (e) {
    render(`<div class="empty-state"><div class="icon">⚠️</div><p>Could not load progress.</p></div>`);
  }
}

async function renderLeaderboard() {
  setActiveNav("leaderboard");
  render(`<div class="spinner">Loading leaderboard…</div>`);
  try {
    const lb = await api("/progress/leaderboard");
    const medals = ["🥇","🥈","🥉"];
    render(`
      <div class="section-head"><h2>🏆 Leaderboard</h2></div>
      <p style="color:var(--text-dim);margin-bottom:16px">Top students by total best quiz scores.</p>
      ${lb.length ? `
        <table class="lb-table">
          <tr><th>Rank</th><th>Student</th><th>Total Score</th><th>Quizzes</th><th>Lessons Done</th></tr>
          ${lb.map((e, i) => `
            <tr class="${state.user && e.user_id===state.user.id ? 'lb-you' : ''}">
              <td>${i<3 ? `<span class="rank-medal">${medals[i]}</span>` : `<span style="color:var(--text-dim)">${i+1}</span>`}</td>
              <td>${state.user && e.user_id===state.user.id ? `<strong>You</strong>` : `User #${e.user_id}`}</td>
              <td><strong style="color:var(--accent)">${e.total_score.toFixed(0)}</strong></td>
              <td>${e.attempts}</td>
              <td>${e.lessons_completed}</td>
            </tr>`).join("")}
        </table>` : `<div class="empty-state"><div class="icon">🏆</div><p>No quiz attempts yet. Be the first on the board!</p></div>`}
    `);
  } catch (e) {
    render(`<div class="empty-state"><div class="icon">⚠️</div><p>Could not load leaderboard.</p></div>`);
  }
}

function renderAuth(mode) {
  setActiveNav("");
  const isLogin = mode === "login";
  render(`
    <div class="auth-card">
      <h2>${isLogin ? "Welcome Back" : "Create Your Account"}</h2>
      <p class="sub">${isLogin ? "Log in to track your progress." : "Start learning DSA today."}</p>
      <form onsubmit="handleAuth(event,'${mode}')">
        ${!isLogin ? `<div class="form-group"><label>Name</label><input id="name" required placeholder="Your name" /></div>` : ""}
        <div class="form-group"><label>Email</label><input id="email" type="email" required placeholder="you@example.com" /></div>
        <div class="form-group"><label>Password</label><input id="password" type="password" required minlength="6" placeholder="Min 6 characters" /></div>
        <div class="form-error" id="authError"></div>
        <button type="submit" class="btn btn-primary" style="width:100%;margin-top:8px">${isLogin ? "Login" : "Sign Up"}</button>
      </form>
      <div class="form-switch">
        ${isLogin ? "Don't have an account? <a onclick=\"navigate('register')\">Sign up</a>"
                  : "Already have an account? <a onclick=\"navigate('login')\">Login</a>"}
      </div>
    </div>
  `);
}

async function handleAuth(e, mode) {
  e.preventDefault();
  const errEl = document.getElementById("authError");
  errEl.textContent = "";
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const body = isLoginBody(mode, email, password);
  try {
    const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
    const data = await api(endpoint, { method: "POST", body: JSON.stringify(body) });
    setAuth(data.access_token, data.user);
    renderNavAuth();
    toast(mode === "login" ? "Welcome back!" : "Account created! 🎉");
    navigate("home");
    // load completed lessons in background
    if (state.user) loadCompletedLessons();
  } catch (e) {
    errEl.textContent = e.detail || "Authentication failed";
  }
}

function isLoginBody(mode, email, password) {
  if (mode === "login") return { email, password };
  const name = document.getElementById("name").value;
  return { name, email, password };
}

async function loadCompletedLessons() {
  if (!state.user) return;
  try {
    const data = await api("/progress/lessons");
    state.completedLessons = new Set(data.completed_lessons || []);
  } catch (e) {}
}

// ---------- Init ----------
(async function init() {
  // Restore session
  const savedUser = localStorage.getItem(USER_KEY);
  if (savedUser) state.user = JSON.parse(savedUser);
  renderNavAuth();

  // Validate token if present
  if (getToken()) {
    try {
      const me = await api("/auth/me");
      state.user = me;
      localStorage.setItem(USER_KEY, JSON.stringify(me));
      renderNavAuth();
      loadCompletedLessons();
    } catch (e) {
      clearAuth();
      renderNavAuth();
    }
  }

  // Initial route
  navigate("home");
})();
