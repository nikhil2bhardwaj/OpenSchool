# Verification Checks — Automated vs Manual

> Generated after static + HTTP audit of `GitHubDeploy` (78 labs).
> Live browser click-through was BLOCKED (desktop browser disconnected) —
> items below marked MANUAL still need a human pass at `http://localhost:8000/`.

## Checked (PASS, static + HTTP)

- [x] Catalog: 78 entries, required fields present, no duplicate ids/hrefs, 78/78 hrefs resolve, 0 `ready=false`
- [x] Hub CATALOG matches `manifests/catalog.json` (78 ids, order match, all hrefs embedded)
- [x] Labs (79 files = 78 + template): CSS `<link>` resolves 0 broken; all `<script src>` resolve 0 broken (storage, ai-examiner, perf, i18n, quiz-bank-1..5, quiz, procedure, report, graph, tts, bookmarks)
- [x] Hub backlinks present in all labs; hub↔exam/formulas/mistakes/teacher-dashboard/tests linked both ways (tests link fixed in footer)
- [x] No CDN `src` in labs (only allowed `http://localhost:11434` placeholder); 0 `Math.random` / `Date.now` in `labs/**`
- [x] Filter/search logic simulated: All=78 → Class 11=24 → Class 11+Biology=4 → reset=78; query `doppler` = 1 hit (`labs/class11/physics/doppler_effect.html`)
- [x] Lab structure present (spot-checked density + doppler): canvas, `#btnRecord`, `#obsTable`, tabs theory/errors/viva/procedure/quiz, back-to-hub
- [x] All 5 pages HTTP 200 with resolving assets + back-to-hub; inline scripts pass `node --check`
- [x] Feature wiring present: mastery/mistakes/planner/tts/bookmarks hooks, procedure init, report/graph includes

## Needs manual check (browser disconnected)

- [ ] Open `/` — 78 cards render, `resultCount` shows 78, zero console errors
- [ ] Click Class 11 + Biology filters — counts drop (24 → 4); All resets to 78
- [ ] Search `Doppler` — single card filters correctly
- [ ] Launch first lab — canvas visible, no console errors; Record appends obsTable row; stats update
- [ ] Switch Theory / Errors / Viva / Quiz / Procedure tabs — each panel displays
- [ ] Complete a Viva + MCQ Quiz — scores save (IndexedDB), mistakes recorded, XP awarded
- [ ] Visit `/teacher-dashboard.html`, `/exam.html` (start + submit timed paper), `/formulas.html` (search), `/mistakes.html` (clear), `/tests.html` (14/14 pass) — no console errors, hub links work

## How to run

1. `cd GitHubDeploy && python -m http.server 8000`
2. Open `http://localhost:8000/` (or `index.html` via `file://`)
3. Work top-down through MANUAL boxes; note any console text per step.
