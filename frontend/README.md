# ANAVO frontend

Separate React + TypeScript + Vite client. GSAP drives a recorded-reference binary/pixel opening; a procedural canvas planet, lime/purple colors, technical grids and condensed typography follow the supplied references. No Streamlit or Python imports.

Start FastAPI in the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies /health and /api to port 8000. Classical optimization and measured QAOA comparison use the existing JSON contracts. Editing inputs clears stale results. Infeasibility, partial quantum results and API errors are displayed explicitly. No solver results are invented in the client. QAOA comparison can take several seconds; compute requests disable editing until finished.

The intro plays on every page load and refresh; use Replay intro in the footer to repeat it. Reduced-motion settings skip the intro and stop the planet/ticker animations. Appliance tables scroll horizontally on small screens.

```powershell
npm run build
npm run preview
```

Production output: frontend/dist. Host these static files separately and configure your web server to proxy /api and /health to a protected FastAPI service. Vite's development proxy is not included in the production output. The standalone Vite preview also proxies the API for local build verification. Never put secrets in browser environment variables. Google Fonts has system-font fallbacks.

This is a local demo, not an externally deployed frontend. The supplied recording was visually inspected and its opening composition rebuilt with live canvas binary territories, large pixel typography, symbol/pause controls, a purple inversion and a stepped reveal. See docs/OPENING_ANIMATION.md. The reference recording is not shipped or played back by the application.
