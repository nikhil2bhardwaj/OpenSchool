# OpenSchool — NCERT Virtual STEM Laboratory (Offline Edition)

Zero-dependency, offline-first virtual science labs mapped to the NCERT/CBSE
Class 9–12 practical curriculum. **78 experiments** (Physics, Chemistry, Biology)
that run entirely in the browser — no build step, no bundler, no server, no
internet. Copy it to a USB stick and it works.

Live mirror: https://nikhil2bhardwaj.github.io/OpenSchool/
Online (CDN) sibling: https://github.com/nikhil2bhardwaj/OpenSchool-online

## What it is

- `GitHubDeploy/` — the whole app. Open `GitHubDeploy/index.html` and automaticamente you get the hub.
- 78 standalone lab sandboxes (`labs/`), each with simulation, observation
  table with error stats, viva-voce arena, 5-question quiz, procedure wizard,
  and CBSE report export — all computed deterministically in-page.
- Notebook data (trials, viva/quiz scores, bookmarks, XP) lives in browser
  IndexedDB via `assets/js/storage.js`, with in-memory fallback.
- English + Hindi shell and content overlays (`EN` / `हिं` toggle).
- Optional AI examiner: local Ollama or your own API key (opt-in, never stored).

## How to use (offline)

**Option A — double-click (works offline):**
1. Download or copy this repository (or just the `GitHubDeploy/` folder) to the computer / USB stick.
2. Open `GitHubDeploy/index.html` in Chrome, Edge, Firefox, or Safari.
3. Pick Class / Subject filters or search, click **Launch Lab →**.

**Option B — local server (recommended, full experience):**
```powershell
cd GitHubDeploy
python -m http.server 8000
```
Then open `http://localhost:8000/`.

**In a lab:** adjust sliders → **Record Reading** (4+ readings) → check mean/error →
**Save to Notebook** → try **Viva**, **Quiz**, **Procedure** tabs → **Export CBSE
Sheet** or **Print Report** for submission.

**For teachers:** open `teacher-dashboard.html` (linked in hub footer) to see
per-experiment trials and viva averages on that machine, export/import JSON.
`exam.html` runs a timed 30-mark practical paper; `formulas.html` is the
class-wise equation sheet; `tests.html` runs the simulation-kernel self-tests.

## Repo layout

```
GitHubDeploy/
├── index.html            # hub (78 cards, filters, search, widgets)
├── teacher-dashboard.html / exam.html / formulas.html / mistakes.html / tests.html
├── manifests/catalog.json# 78 entries: id, cls, subject, archetype, title, aim, ready, href
├── assets/css/           # lab-theme.css (ledger design), tokens.css
├── assets/js/            # storage, quiz/procedure/viva banks (+Hindi), i18n, mastery,
│                         # planner, report, graph, TTS, bookmarks, perf, motion
├── assets/vendor/gsap/   # GSAP vendored locally (no CDN — offline safe)
└── labs/                 # 78 experiments + template_lab.html
```

`Skills/` (design references) and `Backup/` (pre-redesign snapshot) are not
part of the app and are not published.

## Notes

- Deterministic simulations only — no random physics; the LLM role is tutor/examiner, never number generator.
- Dark ledger UI; Hindi covers hub/shell/quiz/viva/procedure/catalog (theory paragraphs stay English).
- `PROJECT_SUMMARY.md`, `ULTIMATE_STEM_LAB_CHECKLIST.md`, `Checks.md` document scope and verification.
- Open-source, free for educational use.
