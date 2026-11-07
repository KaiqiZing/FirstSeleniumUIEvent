# Contributing

[简体中文](./CONTRIBUTING.md) | **English**

Thanks for helping improve the Selenium UI Failure Playground. This project is a **practice range** for Selenium Web UI automation: the pages faithfully reproduce failures seen in real systems, while the answers live only in the READMEs. Keep the two separated.

## 1. Ways to contribute

| Type | Good fit |
| --- | --- |
| Report a problem | A scenario cannot be reproduced, a page errors out, or an assertion anchor is ambiguous |
| Add a scenario | Cover a high-frequency problem not yet in the README (open an Issue first to align) |
| Improve docs | Fix reproduction steps, complete the API contract, refine the "cannot be reproduced" list |
| Polish the platform | Frontend styling, navigation structure, backend stability — anything non-scenario |

## 2. Reporting an Issue

Please include:

1. **The route** involved, e.g. `/i/17`, `/e/03`.
2. **Environment**: OS, browser and version, WebDriver version, Node / Python versions.
3. **Steps to reproduce** and **expected vs. actual** results (the text in the "Operation Result" panel is the most useful).
4. Screenshots or console errors where relevant.

Never paste real business data, internal system addresses or credentials into an Issue. All sample data here is fictitious.

## 3. Submitting code (Pull Request)

```bash
# 1. Fork, then work locally
git clone https://github.com/<your-name>/FirstSeleniumUIEvent.git
cd FirstSeleniumUIEvent

# 2. Create a branch (feat / fix / docs / chore prefix)
git checkout -b feat/scenario-i19

# 3. Test locally, then commit
git add .
git commit -m "feat: add scenario I-19 (nested scroll in table)"

# 4. Push and open a PR
git push origin feat/scenario-i19
```

PR requirements:

- One PR does one thing; do not mix formatting, refactoring and a new scenario.
- Make sure both servers start (`python app.py` / `npm run dev`) before submitting; config or dependency changes must also pass `npm run build`.
- Describe the change, the affected scenario codes and how you tested it.

Commit messages follow Conventional Commits: `feat:` new scenario or feature, `fix:` bug fix, `docs:` documentation, `refactor:` refactor, `chore:` housekeeping.

## 4. The four files a new scenario must touch

Adding `I-19`, for example — miss any of these and you get either "the nav links to a 404" or "the page exists but is undocumented":

1. **Scenario catalog**: `frontend/src/data/scenarios.js`
   Append `{ code, group, file, title, desc }` to the matching group. This file is the **single source of truth** for navigation, home cards and route registration.
2. **Page component**: `frontend/src/views/<group>/<file>.vue`
   Keep the naming style (e.g. `19-nested-scroll.vue`).
3. **Backend API** (if needed): `backend/api/xxx_api.py`
   A new `Blueprint` must be registered in `register_blueprints` inside `backend/api/__init__.py`; everything is mounted under `/api`.
4. **Documentation**: the project maintains English and Chinese READMEs and **both must be updated together**:
   - Add a row to the scenario catalog table in section 2 of both [README.md](./README.md) and [README.zh-CN.md](./README.zh-CN.md).
   - Add reproduction steps and Selenium notes to section 3.
   - Register any new endpoint in section 4.

## 5. Coding conventions

### Frontend

- Vue 3 `<script setup>` plus Element Plus. Do not introduce another UI framework or a state-management library.
- Keep styles `scoped` or reuse variables from `src/styles`; avoid global selectors that leak into other scenarios.
- **No solution hints, locator suggestions or "correct answer" copy on the page.** It must look like a broken real system, not a tutorial.
- Emit operation results into the "Operation Result" panel at the bottom of the page; Selenium scripts assert against it. Do not rely solely on the auto-dismissing `ElMessage` toast.

### Backend

- Uniform envelope: `{ "code": 0, "data": ..., "message": "..." }` with `code=0` meaning success; register business error codes in the README.
- Keep tunable values (delays, timeouts, failure rates, page sizes) in `backend/config.py`; no magic numbers in business code.
- Data must be repeatable: in-memory state or resettable SQLite tables. Returning to the initial state after a Flask restart is a design goal, not a bug.
- Add new dependencies to `backend/requirements.txt` (Python) or `frontend/package.json` (Node).

### Naming and numbering

- Keep the existing group prefixes: `I-` interaction, `W-` waiting, `M-` multi-window, `C-` compatibility, `X-` misc, `E-` crypto. Never reuse or reorder numbers.
- Routes derive from `group` and `code` (e.g. `I-19` → `/i/19`); do not hand-write route entries.

## 6. What not to commit

Already covered by `.gitignore` — do not force-add:

- `backend/data/` (SQLite databases, rebuilt on first start)
- `.venv/`, `backend/.SeleniumUIEvent/`, `__pycache__/`, `*.pyc`
- `node_modules/`, `frontend/dist/`
- `*.log`, `.env`, `.DS_Store`, `.idea/`, `.vscode/`

## 7. License

Released under the [MIT License](./LICENSE). Submitting a PR means you agree your contribution is published under the same license.
