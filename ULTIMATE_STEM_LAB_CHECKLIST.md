# Ultimate Virtual STEM Lab — Vision & Pre-Redesign Checklist

> Reference for the OpenSchool NCERT Virtual STEM Laboratory.
> Redesign with `Skills/` must stay vendored-local, no CDN, per
> `Project Master Brief & Architectural Non-Negotiables.md:16`
> (zero-build, pure static, `file:///` + GitHub Pages compatible).
> Skills (GSAP / Three.js / motion / UI-UX) are used as *patterns*
> re-implemented in pure CSS + canvas — no npm, no bundler, no CDN.

## Vision

Offline-first, NCERT-mapped, zero-build (`GitHubDeploy/index.html` hub + 78 labs).
A student opens `index.html` from USB, no internet, and gets:

- Curriculum hub with search, Class / Subject / Biology filters,
  progress ring per lab (IndexedDB), "continue where you left off".
- Every lab feels like real apparatus: animated diagram (canvas),
  drag/slide controls with live readout, Record → observation table →
  mean/error auto-calc → Save to IndexedDB → CBSE export/print.
- Learn loop per lab: Theory → Simulate → Record → Viva (offline graded)
  → 5-MCQ Quiz (`assets/js/quiz-bank-1..5.js` + `quiz.js`) → AI examiner
  opt-in (local Ollama / user cloud key, never stored).
- Teacher view: `teacher-dashboard.html` aggregates local trials/viva,
  export/import JSON, print. Privacy-safe, no server.
- Universal: responsive, keyboard + screen-reader clean, EN/HI shell
  (`assets/js/i18n.js`), light/dark, `tests.html` kernels green.
- Deterministic physics only in JS (RK4 / closed-form / FSM). LLM never
  generates numbers — Socratic tutor / viva examiner only.

## Pre-Redesign Checklist

### Correctness / completeness

- [ ] Catalog = 78/78 hrefs resolve; `index.html` inline CATALOG matches `manifests/catalog.json`
- [ ] All 78 labs full-template: stage + readout + obsTable + stats + Save/Export + Theory/Errors/Viva/Quiz tabs + `storage.js` + `ai-examiner.js`
- [ ] Determinism: 0 `Math.random` / `Date.now` in `labs/**`; Bohr ASCII-only math
- [ ] Fix `PROJECT_SUMMARY.md:143` stale "70 entries" → 78

### Student learning

- [ ] 390 MCQs verified (78 IDs × 5 resolve, 1 correct answer each, explanations)
- [ ] Viva banks 4 Qs/lab with model answers + grading thresholds sane
- [ ] Per-lab Theory equations + precautions/errors filled (no lorem)
- [ ] CBSE export sheet renders tables + results correctly

### Persistence / teacher

- [ ] `storage.js:exportDB/importDB/getUsageStats` round-trip tested
- [ ] Dashboard shows trials/viva avg, import rejects bad JSON, print works

### Access / quality

- [ ] Responsive 360px → desktop, canvas scales, tables scroll-x
- [ ] A11y: skip-link, tab roles, aria-labels, focus-visible, contrast ≥ 4.5:1, `prefers-reduced-motion`
- [ ] Perf: `perf.js` rAF throttle on all slider inputs, no continuous RAF loops when idle
- [ ] i18n shell EN/HI toggles hub + template without breakage
- [ ] Dark/light toggle persists; `100% Offline` badge present
- [ ] `tests.html` 14/14 pass; storage-guard on 79/79 files (78 labs + template)

## Process

1. Implement + verify every box above (static grep + browser click-through).
2. Only then start visual redesign (UI, motion, diagrams) using `Skills/`
   patterns re-implemented offline-first.

## Phase 2 — New Ultimate Features (implemented)

All offline-first, zero-build, deterministic, IndexedDB-backed.

- [x] F1 Mastery & streaks: XP per trial/viva/quiz, badges, progress rings on hub (`assets/js/mastery.js`)
- [x] F2 Exam Mode: timed CBSE-pattern practical exam, random viva+MCQ set, marking scheme (`exam.html`)
- [x] F3 Mistake Book: auto-collect wrong viva/MCQ answers, retry queue (`assets/js/mistakes.js` + `mistakes.html`)
- [x] F4 Lab Report Builder: one-click CBSE report with readings + stats + canvas snapshot (`assets/js/report.js`)
- [x] F5 Graph & curve-fit toolkit: best-fit slope/intercept/R² (`assets/js/graph.js`)
- [x] F6 Procedure Wizard: step-by-step lab-manual mode (`assets/js/procedure.js` + `procedure-bank.js`, 78 IDs)
- [x] F7 Formula Sheet hub: class-wise equations (`formulas.html`)
- [x] F8 Revision Planner: spaced-repetition queue (`assets/js/planner.js` + hub widget)
- [x] F9 Read-aloud: offline TTS via SpeechSynthesis (`assets/js/tts.js`)
- [x] F10 Bookmarks: star theory/viva/MCQ to review notebook (`assets/js/bookmarks.js` + storage extension)
