# Spend Tracker

🚀 **Live Application:** https://spend-tracker-1-ip12.onrender.com
📖 **API Documentation:** [https://spend-tracker-1.onrender.com/docs](https://spend-tracker-1.onrender.com/docs)

A small service for logging expenses and viewing spend summaries, with a lightweight
two-page HTML/JS frontend (Expenses, Summary).

## How to run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/` in a browser for the UI, or use the API directly.

All endpoints require an `X-API-Key` header. The default key is `dev-local-key` (set via the
`SPEND_TRACKER_API_KEY` env var). The database is a SQLite file (`spend_tracker.db`) created
automatically in the working directory on first run; override its location with `DATABASE_URL`.

### Example requests

```bash
curl -X POST http://localhost:8000/expenses \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-local-key" \
  -d '{"amount": 42.50, "category": "food", "note": "lunch", "date": "2026-09-10"}'

curl "http://localhost:8000/expenses?category=food" -H "X-API-Key: dev-local-key"

curl -X PUT http://localhost:8000/expenses/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-local-key" \
  -d '{"amount": 50, "category": "food", "note": "corrected", "date": "2026-09-10"}'

curl -X DELETE http://localhost:8000/expenses/1 -H "X-API-Key: dev-local-key"

curl "http://localhost:8000/summary?month=2026-09" -H "X-API-Key: dev-local-key"
```

## How to run tests

```bash
pytest
```

Tests use an in-memory SQLite database, isolated from the dev database, and cover:
- Expense creation (happy path + invalid amount/category/date, missing/wrong API key,
  category normalization — trimming and case-folding — and rejection of whitespace-only categories)
- Listing with category and date-range filters (individually and combined), pagination
  (including the upper `limit` bound and echoed `limit`/`offset`), and no-match cases
- Update/delete: happy path, 404 on a missing id, validation on update, and auth checks
- The distinct-categories endpoint: empty list, sorted/deduplicated output, auth check
- Summary totals, per-category breakdown (including merging categories that only differ by
  case/whitespace), month-over-month change (including the no-prior-month edge case), and the
  category spike insight (over/under/exactly the 20% threshold, and a brand-new category with
  no prior-month data, which is excluded rather than reported as an infinite spike)

## API

- `POST /expenses` — create an expense. Body: `{amount, category, note?, date}`.
  `amount` must be > 0, `category` non-empty after normalization, `date` an ISO date (`YYYY-MM-DD`).
  Category values are trimmed and lowercased server-side (see Design decisions).
- `GET /expenses?category=&start_date=&end_date=&limit=&offset=` — list expenses. All filters
  are optional and combinable; `category` is matched case-insensitively. `limit` (default 50,
  max 200) and `offset` paginate the results. Returns `{items, total, limit, offset}`.
- `PUT /expenses/{id}` — full replace of an expense's fields. Same validation as create. 404 if
  the id doesn't exist.
- `DELETE /expenses/{id}` — delete an expense. 204 on success, 404 if the id doesn't exist.
- `GET /expenses/categories` — sorted, deduplicated list of every category currently in use.
  Backs the add/filter-form autocomplete.
- `GET /summary?month=YYYY-MM` — defaults to the current month. Returns total spend, spend by
  category, month-over-month change, and any category flagged for a >20% spend increase versus
  the previous month (categories with no prior-month spend are excluded from this check, since
  a percent increase from zero is undefined).

## Key design decisions

- **SQLite via SQLAlchemy**, not an in-memory list, so the schema (`Expense` table with indexes
  on `category` and `date`) is a real, inspectable artifact and queries scale past a toy dataset.
- **Pydantic validation** on the request schema (`amount > 0`, non-empty `category`, valid date)
  keeps validation declarative and lets FastAPI's built-in 422 handling do the work, rather than
  hand-rolling checks.
- **Two static HTML pages** (Expenses, Summary) sharing `styles.css`/`app.js`, served directly by
  FastAPI via `StaticFiles` — no build step or separate dev server, the whole app runs from one
  `uvicorn` command, but the UI isn't crammed onto a single screen either.
- **Header-based API key** (`X-API-Key`) as a lightweight stand-in for real auth, sufficient to
  demonstrate an authenticated boundary without the overhead of a full user/token system.
- **Category normalization** (`app/utils.py::normalize_category`, used in both the Pydantic
  validator and the `GET /expenses` filter): categories are trimmed and lowercased before being
  stored or matched. Without this, "Food", " food ", and "FOOD" would silently fragment
  `spend_by_category` and the spike insight into separate buckets, and an exact-match filter
  would miss casually-typed variants.
- **`GET /expenses/categories`** exists purely to back the add/filter-form autocomplete with the
  full set of categories in use, rather than deriving suggestions from whatever page of results
  happens to be loaded client-side.
- **Repository pattern** (`app/repository.py`): all SQLAlchemy query logic lives behind
  `ExpenseRepository`, so route handlers and services depend on a small, intention-revealing
  interface (`add`, `list`, `spend_by_category`) rather than raw ORM queries. This keeps
  persistence details in one place and makes it easy to swap in a different store or a test
  double later.
- **Strategy pattern for insights** (`app/insights.py`): the category-spike check implements an
  `Insight` interface (`evaluate(current, previous) -> findings`). `SummaryService` holds a list
  of insights and asks each one to evaluate the same current/previous category aggregates it
  already computed. Adding a new insight (e.g. a budget-threshold alert) means writing one new
  class and registering it — `SummaryService` and the `/summary` route don't change.
- **Service layer** (`app/summary_service.py`): `SummaryService` composes the repository and the
  registered insights to build the `/summary` response, keeping that orchestration out of the
  route handler (`app/main.py`), which only wires dependencies and maps to HTTP.

## What I'd do differently with more time

- Real authentication (JWT with token expiry, or a proper API key store, plus per-user accounts
  and data isolation) instead of one shared static key.
- Sorting options on `GET /expenses` (currently fixed to most-recent-first); results are already
  paginated.
- Alembic migrations instead of `create_all`, so schema changes are versioned.
- Multi-currency support (amounts are currently assumed to be a single implicit currency).
- Structured logging and a global exception handler for cleaner error responses.
- Deployment to a public URL (Render/Fly.io) with the SQLite file on a persistent volume, or a
  move to Postgres for a real multi-user deployment.
- Richer insights (spend trend over multiple months, budget thresholds) beyond the single
  category-spike check.
- Version control: this project isn't currently in a git repository.
