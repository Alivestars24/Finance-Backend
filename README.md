# Finance Data Processing and Access Control Backend

A role-based financial records management API built with **FastAPI**, **SQLAlchemy**, and **SQLite**. Designed with a clean separation of concerns thin HTTP routers delegating to dedicated service functions so the system is easy to read, test, and extend.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Assumptions Made](#assumptions-made)
- [Setup and Running Locally](#setup-and-running-locally)
- [API Reference](#api-reference)
- [Full Test Flow (Swagger UI)](#full-test-flow-swagger-ui)
- [Role-Based Access Control](#role-based-access-control)
- [Design Decisions and Tradeoffs](#design-decisions-and-tradeoffs)

---

## Features

- **User management** — create users, assign roles (`admin`, `analyst`, `viewer`), manage active status
- **JWT authentication** — token-based login with role embedded in the payload
- **Financial records CRUD** — create, retrieve, and filter income/expense entries
- **Dashboard analytics** — total income, total expenses, net balance, and category-wise breakdowns
- **Role-based access control** — enforced at the middleware level; each endpoint declares which roles are permitted
- **Input validation** — Pydantic schemas enforce correct types, enum values, and required fields
- **Meaningful error responses** — appropriate HTTP status codes with descriptive error messages throughout
- **Swagger UI** — interactive API documentation available out of the box at `/docs`
- **Modular architecture** — routers handle HTTP, services handle business logic, models handle data

---

## Architecture

The system is organized into following clear layers:

<img width="793" height="805" alt="image" src="https://github.com/user-attachments/assets/820ff646-2a87-4f39-acc1-a206b6aaeb9c" />


**Why this structure?**

Routers only deal with HTTP concerns (extracting path params, query params, request bodies, injecting dependencies). All actual logic database queries, aggregations, token creation lives in the service layer. This means you can test service functions in isolation without spinning up an HTTP server, and you can swap a router implementation (e.g. switching from REST to GraphQL) without touching the business logic at all.

<img width="606" height="651" alt="image" src="https://github.com/user-attachments/assets/d7f53988-3e2a-4117-89bf-a124e182d7ea" />

**Sequence Diagram:**
<img width="706" height="702" alt="image" src="https://github.com/user-attachments/assets/1aeaa614-8e5d-402b-b71a-ff1099b070ea" />

---

## Project Structure

```
finance-backend/
│
├── app/
│   ├── main.py              # App entry point, router mounting, DB init
│   ├── database.py          # SQLAlchemy engine and session setup
│   ├── models.py            # ORM models: User, Record
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── dependencies.py      # JWT decoding, role enforcement dependency
│   ├── auth.py              # Password hashing, JWT token creation
│   │
│   ├── routers/             # HTTP layer — routes only, no business logic
│   │   ├── auth.py          # POST /auth/login
│   │   ├── users.py         # POST /users/, GET /users/
│   │   ├── records.py       # POST /records/, GET /records/
│   │   └── dashboard.py     # GET /dashboard/summary, /dashboard/category
│   │
│   └── services/            # Business logic layer
│       ├── auth_service.py       # login_user()
│       ├── user_service.py       # create_user(), list_users()
│       ├── record_service.py     # create_record(), get_records()
│       └── dashboard_service.py  # get_summary(), get_category_breakdown()
│
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (`finance.db`) |
| Auth | JWT via `python-jose`, bcrypt via `passlib` |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Docs | Swagger UI (built into FastAPI at `/docs`) |
| Python | 3.11 |

---

## Assumptions Made

1. **SQLite as the database** — chosen for simplicity and zero-configuration setup. The SQLAlchemy ORM means switching to PostgreSQL or MySQL requires changing only the `DATABASE_URL` string in `database.py`. No other code changes needed.

2. **Records are owner-scoped** — each financial record belongs to a specific user (`owner_id`). All read and dashboard operations return only records belonging to the currently authenticated user. Admins can create records on behalf of other users by passing `owner_id` explicitly in the request body.

3. **No soft delete** — records and users are hard-deleted if removed. Soft delete (an `is_deleted` flag) is a straightforward extension if needed.

4. **`POST /users/` is open** — user creation does not require authentication. In a production system this would typically be admin-only or handled via an invite flow. This design choice prioritizes ease of testing and evaluation.

5. **Single token type** — the JWT access token does not have a refresh token counterpart. Tokens expire in 2 hours. A refresh token flow would be the natural next step.

6. **Dashboard is user-scoped** — summary and category breakdown reflect only the authenticated user's records, not a global aggregate. This matches the "finance dashboard" framing in the brief.

---

## Setup and Running Locally

### Prerequisites

- Python 3.11 installed

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd finance-backend
```

### Step 2 — Create and activate a virtual environment

```bash
# Windows
py -3.11 -m venv venv
venv\Scripts\activate

# macOS / Linux
python3.11 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Start the server

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://127.0.0.1:8000`.

### Step 5 — Open Swagger UI

Navigate to `http://127.0.0.1:8000/docs` to explore and test all endpoints interactively.

> **Note:** The SQLite database file (`finance.db`) is created automatically in the project root on first startup. No database setup or migration commands are needed.

---

## API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | None | Login with username and password. Returns a JWT access token. |

**Request body** (form data):
```
username: <string>
password: <string>
```

**Response:**
```json
{
  "access_token": "<jwt_token>"
}
```

---

### Users

| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| POST | `/users/` | None | — | Create a new user |
| GET | `/users/` | JWT | admin | List all users |

**Create user — request body:**
```json
{
  "username": "alice",
  "password": "securepass",
  "role": "analyst"
}
```
Role must be one of: `viewer`, `analyst`, `admin`.

---

### Financial Records

| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| POST | `/records/` | JWT | admin | Create a financial record |
| GET | `/records/` | JWT | admin, analyst, viewer | List records with optional filters |

**Create record — request body:**
```json
{
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "notes": "Monthly salary",
  "owner_id": null
}
```

- `type` must be `income` or `expense`
- `owner_id` is optional — if omitted, the record is assigned to the authenticated user. Admins can set this to another user's ID to create records on their behalf.

**Get records — query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `skip` | integer | Pagination offset (default: 0) |
| `limit` | integer | Max records to return (default: 10) |
| `category` | string | Filter by category (e.g. `salary`, `rent`) |
| `type` | string | Filter by `income` or `expense` |

---

### Dashboard

| Method | Endpoint | Auth | Roles | Description |
|---|---|---|---|---|
| GET | `/dashboard/summary` | JWT | admin, analyst | Total income, expense, and net balance |
| GET | `/dashboard/category` | JWT | admin, analyst | Per-category totals |

**Summary response:**
```json
{
  "total_income": 8000.0,
  "total_expense": 2500.0,
  "net_balance": 5500.0
}
```

**Category breakdown response:**
```json
[
  { "category": "salary", "total": 8000.0 },
  { "category": "rent", "total": 1500.0 },
  { "category": "utilities", "total": 1000.0 }
]
```

---

## Full Test Flow (Swagger UI)

This walkthrough exercises every endpoint and all three roles. Follow the steps in order.

---

### Step 1 — Create an admin user

**Endpoint:** `POST /users/`

```json
{
  "username": "admin1",
  "password": "1234",
  "role": "admin"
}
```

Expected: `200 OK` with the created user object.

---

### Step 2 — Create an analyst user

**Endpoint:** `POST /users/`

```json
{
  "username": "analyst1",
  "password": "1234",
  "role": "analyst"
}
```

---

### Step 3 — Create a viewer user

**Endpoint:** `POST /users/`

```json
{
  "username": "viewer1",
  "password": "1234",
  "role": "viewer"
}
```

---

### Step 4 — Login as admin

**Endpoint:** `POST /auth/login`

Fill the form fields:
```
username: admin1
password: 1234
```

Copy the `access_token` from the response.

---

### Step 5 — Authorize in Swagger

Click the **Authorize** button (top right of Swagger UI).

Enter:
```
username: admin1
password: 1234
```

Click **Authorize**, then **Close**. All subsequent requests will send the JWT automatically.

---

### Step 6 — Create records as admin

**Endpoint:** `POST /records/`

Create a few records to populate the dashboard:

```json
{
  "amount": 5000,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "notes": "Monthly salary"
}
```

```json
{
  "amount": 1500,
  "type": "expense",
  "category": "rent",
  "date": "2026-04-02",
  "notes": "April rent"
}
```

To create a record for a different user (e.g. analyst1 whose ID is `2`), add `"owner_id": 2` to the request body.

---

### Step 7 — Fetch your records

**Endpoint:** `GET /records/`

Returns all records belonging to the logged-in user. Try the optional filters:
- `?type=income` — only income records
- `?category=rent` — only rent records
- `?skip=0&limit=5` — paginate results

---

### Step 8 — View dashboard summary

**Endpoint:** `GET /dashboard/summary`

Expected:
```json
{
  "total_income": 5000.0,
  "total_expense": 1500.0,
  "net_balance": 3500.0
}
```

---

### Step 9 — View category breakdown

**Endpoint:** `GET /dashboard/category`

Expected:
```json
[
  { "category": "salary", "total": 5000.0 },
  { "category": "rent", "total": 1500.0 }
]
```

---

### Step 10 — Test role enforcement

Log out by clicking **Authorize → Logout** in Swagger, then log in as `viewer1`.

Try accessing `POST /records/` — you should receive:
```json
{ "detail": "Forbidden" }
```
with a `403` status code.

Try accessing `GET /dashboard/summary` — also `403`. Viewers can only access `GET /records/`.

Repeat by logging in as `analyst1` — they can access records and dashboard, but cannot create records (`POST /records/` returns `403`).

---

## Role-Based Access Control

| Endpoint | viewer | analyst | admin |
|---|---|---|---|
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `POST /users/` | ✅ | ✅ | ✅ |
| `GET /users/` | ❌ | ❌ | ✅ |
| `POST /records/` | ❌ | ❌ | ✅ |
| `GET /records/` | ✅ | ✅ | ✅ |
| `GET /dashboard/summary` | ❌ | ✅ | ✅ |
| `GET /dashboard/category` | ❌ | ✅ | ✅ |

### How enforcement works

The `require_roles()` function in `dependencies.py` is a FastAPI dependency factory. Each router endpoint declares which roles are permitted:

```python
user = Depends(require_roles(["admin", "analyst"]))
```

When a request arrives, FastAPI first decodes the JWT via `get_current_user`, extracts the `role` field from the payload, and checks it against the allowed list. If the role is not permitted, a `403 Forbidden` response is returned before the route function executes. Business logic is never reached for unauthorized roles.

---

## Design Decisions and Tradeoffs

### Router / Service separation

Routers are intentionally kept thin — they handle only HTTP-level concerns (parsing request bodies, query parameters, calling `Depends`). All database queries, aggregations, and logic live in the service layer. This makes services independently testable and keeps routers readable at a glance.

### SQLite over a hosted database

SQLite requires zero infrastructure to run, making the project immediately runnable for any evaluator. The ORM abstraction means a production switch to PostgreSQL is a one-line change (`DATABASE_URL`).

### JWT with role in payload

The user's role is embedded in the JWT at login time. This avoids a database round-trip on every request for role checking. The tradeoff is that a role change does not take effect until the user's current token expires (2 hours). For a production system, shorter token lifetimes or token revocation lists would address this.

### Pydantic field validation

`role` accepts only `viewer | analyst | admin` and `type` accepts only `income | expense`, enforced via `Field(pattern=...)`. Invalid values are rejected at the schema layer before any database interaction occurs, returning a clear `422 Unprocessable Entity` with the field name and reason.

### No soft delete

Records are permanently deleted when removed. Adding soft delete (an `is_deleted: bool` column + filtering it out of all queries) is a small, contained change if needed. Keeping it out simplified the initial implementation without sacrificing anything the brief required.
