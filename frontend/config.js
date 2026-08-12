/* ============================================================
   Frontend runtime configuration.
   ------------------------------------------------------------
   The API base URL is resolved in this order:
     1. window.__API_BASE__  -> set at deploy time (see build.sh /
        Render static-site build command) so the SPA points at the
        public Kong gateway URL on Render.
     2. "" (same-origin)     -> default for local docker-compose runs,
        where the gateway serves both the UI and the API on one origin.

   To deploy on Render, set the build command for the static site to:
        bash build.sh
   and set the env var  API_BASE_URL=https://kong-gateway-xxxx.onrender.com
   on the static site. build.sh rewrites config.js accordingly.
   ============================================================ */

window.__API_BASE__ = window.__API_BASE__ || "";
