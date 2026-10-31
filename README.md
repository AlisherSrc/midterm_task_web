# 🚀 Space Bounty Hunters — REST API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker)](https://www.docker.com/)
[![Postman](https://img.shields.io/badge/Postman-Collection_v2.1-FF6C37?logo=postman)](https://www.postman.com/)

A cloud-native REST API developed for interplanetary bounty hunters. The system provides access to a database of wanted galactic criminals and a mission journal recording bounty hunting encounters and capture attempts.

Built with **FastAPI** and **PostgreSQL** using **SQLAlchemy 2.0** ORM and **Pydantic v2**.

---

## 📋 Table of Contents
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Database Models & Relationship](#-database-models--relationship)
- [Quick Start Guide](#-quick-start-guide)
  - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
  - [Option B: Local Setup & Manual Run](#option-b-local-setup--manual-run)
- [Database Setup & Seed Data Import](#-database-setup--seed-data-import)
- [REST API Reference](#-rest-api-reference)
  - [Wanted Criminals API](#1-wanted-criminals-api)
  - [Bounty Hunting Journal API (CRUD)](#2-bounty-hunting-journal-api-crud)
- [Postman Collection](#-postman-collection)
- [Running Automated Tests](#-running-automated-tests)

---

## 🏗️ Architecture & Tech Stack

* **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12 / 3.13)
* **Relational Database:** [PostgreSQL 16](https://www.postgresql.org/)
* **ORM & Query Builder:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
* **Database Driver:** [Psycopg 3 (`psycopg[binary]`)](https://www.psycopg.org/)
* **Data Validation & Serialization:** [Pydantic v2](https://docs.pydantic.dev/)
* **Testing:** [pytest](https://docs.pytest.org/) & `TestClient` (FastAPI/Starlette)
* **Containerization:** Docker & Docker Compose

---

## 🗄️ Database Models & Relationship

### 1. `WantedCriminal` (`wanted_criminals`)
| Column | Type | Constraints / Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment |
| `name` | `VARCHAR(255)` | Real name, Nullable (`NULL` if unknown) |
| `nickname` | `VARCHAR(255)` | Criminal handle / alias, Not Null |
| `reward` | `DOUBLE PRECISION` | Bounty amount in galactic credits |
| `last_known_coordinates`| `TEXT` | Coordinates (lat, lon) and text location note |
| `difficulty` | `INTEGER` | Rating from `1` to `10` (`CHECK (difficulty >= 1 AND difficulty <= 10)`) |
| `armed` | `BOOLEAN` | Whether target is armed and dangerous |
| `has_crew` | `BOOLEAN` | Whether target operates with a crew |
| `escape_master` | `BOOLEAN` | Whether target has high-profile escape history |

### 2. `HuntLog` (`hunt_logs`)
| Column | Type | Constraints / Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment |
| `criminal_id` | `INTEGER` | Foreign Key (`REFERENCES wanted_criminals(id) ON DELETE CASCADE`) |
| `success` | `BOOLEAN` | Whether the capture was successful |
| `notes` | `TEXT` | Mission encounter notes and tactical logs |
| `created_at` | `TIMESTAMPTZ` | **Server-generated timestamp** (`server_default=NOW()`) |

### One-to-Many Relationship
* One **`WantedCriminal`** can have multiple capture attempts (**`HuntLog`** entries).
* Each **`HuntLog`** is linked to exactly one existing criminal via `criminal_id`.
* Cascade on delete guarantees database referential integrity.

---

## ⚡ Quick Start Guide

### Option A: Docker Compose (Recommended)
The fastest way to spin up the entire application with PostgreSQL and seeded data:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd space_bounty_hunters

# 2. Start PostgreSQL and FastAPI Backend
docker compose up --build
```

* **Swagger OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Interactive Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Root Info:** [http://localhost:8000/](http://localhost:8000/)

---

### Option B: Local Setup & Manual Run

#### 1. Configure Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure `.env`
Copy the template or edit `.env`:
```bash
cp .env.example .env
```
Ensure your PostgreSQL credentials in `.env` match your database:
```ini
DB_HOST=localhost
DB_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=space_bounty_hunters
```

#### 3. Run Server
```bash
uvicorn app.main:app --reload --port 8000
```

---

## 💾 Database Setup & Seed Data Import

The project comes pre-configured with **7 wanted criminals** (requirement: >= 5) and **14 journal logs** (requirement: >= 10).

### Method 1: Automatic via Docker
When starting with `docker compose up --build`, the script `db/init.sql` is mounted to `/docker-entrypoint-initdb.d/01-init.sql` and executes automatically on container start.

### Method 2: Manual SQL Import via `psql`
```bash
# Create database
psql -U postgres -c "CREATE DATABASE space_bounty_hunters;"

# Import schema and seed records
psql -U postgres -d space_bounty_hunters -f db/init.sql
```

### Method 3: Python Seeder Script
```bash
# Make sure your virtual environment is active and .env is set
python -m db.seed
```

---

## 📡 REST API Reference

### 1. Wanted Criminals API

#### `GET /api/criminals/`
List wanted criminals with multi-parameter filtering and sorting.

* **Query Parameters:**
  * `min_reward` *(float, optional)*: Minimum bounty threshold.
  * `max_reward` *(float, optional)*: Maximum bounty threshold.
  * `armed` *(bool, optional)*: Filter by armed status (`true` / `false`).
  * `has_crew` *(bool, optional)*: Filter by crew presence (`true` / `false`).
  * `escape_master` *(bool, optional)*: Filter by escape master status (`true` / `false`).
  * `sort` *(string, optional)*: Sort order — `'reward'` (ascending) or `'-reward'` (descending).

* **Example Request:**
  ```http
  GET /api/criminals/?min_reward=5000&armed=true&sort=-reward HTTP/1.1
  Host: localhost:8000
  ```

* **Example Response (200 OK):**
  ```json
  [
    {
      "id": 3,
      "name": null,
      "nickname": "Obsidian Raven",
      "reward": 220000.0,
      "last_known_coordinates": "Kuiper Belt Outpost 88 (-78.112, 12.903) - Deep freeze sector",
      "difficulty": 10,
      "armed": true,
      "has_crew": true,
      "escape_master": true
    },
    {
      "id": 1,
      "name": "Vicious Kane",
      "nickname": "Red Nova",
      "reward": 150000.0,
      "last_known_coordinates": "Sector 4, Kepler-22b (-14.234, 120.451) - Abandoned titanium refinery",
      "difficulty": 9,
      "armed": true,
      "has_crew": true,
      "escape_master": true
    }
  ]
  ```

#### `GET /api/criminals/{id}/`
Retrieve full details and encounter history for a single criminal.
* **Returns:** `200 OK` with criminal info + list of all associated `hunt_logs`.
* **Error:** `404 Not Found` if ID does not exist.

---

### 2. Bounty Hunting Journal API (CRUD)

#### `GET /api/hunts/`
List all hunt logs, sorted by creation date descending.
* **Query Parameters:**
  * `criminal_id` *(int, optional)*: Filter logs by referenced criminal ID (e.g. `/api/hunts/?criminal_id=1`).
* **Returns:** `200 OK` with array of hunt logs.

#### `GET /api/hunts/{id}/`
Retrieve a single hunt log by its unique identifier.
* **Returns:** `200 OK` or `404 Not Found`.

#### `POST /api/hunts/`
Record a new capture attempt.
* **Validation:** Validates that `criminal_id` references an existing criminal in the database.
* **Server Timestamp:** The `created_at` timestamp is **strictly generated on the server**.
* **Request Body:**
  ```json
  {
    "criminal_id": 3,
    "success": false,
    "notes": "Target escaped through an asteroid field."
  }
  ```
* **Returns:** `201 Created` with newly created record including server `created_at` timestamp.
* **Error:** `404 Not Found` if `criminal_id` does not exist.

#### `PATCH /api/hunts/{id}/`
Update `success` and/or `notes` for an existing log.
* **Request Body:**
  ```json
  {
    "success": true,
    "notes": "Target was captured during a secondary strike."
  }
  ```
* **Returns:** `200 OK` with updated record.
* **Errors:** `400 Bad Request` if no update fields supplied, `404 Not Found` if log does not exist.

#### `DELETE /api/hunts/{id}/`
Delete a hunt log permanently.
* **Returns:** `204 No Content`.
* **Error:** `404 Not Found` if log does not exist.

---

## 📮 Postman Collection

An exported Postman Collection is provided in the repository root:
* **File:** [`space_bounty_hunters.postman_collection.json`](space_bounty_hunters.postman_collection.json)
* **Schema:** Postman v2.1.0

### Included Demonstrations:
1. **Criminals:**
   * `List All Criminals`
   * `Filter & Sort: min_reward=5000 & armed=true & sort=-reward` (assignment prompt exact example)
   * `Filter: max_reward=100000 & has_crew=true`
   * `Filter & Sort: escape_master=true & sort=reward`
   * `Get Criminal Details by ID`
   * `[Invalid Request] Criminal Not Found (404)`
   * `[Invalid Request] Invalid Sort Option (400)`
2. **Bounty Hunting Journal (CRUD):**
   * `List All Hunt Logs`
   * `Filter Hunt Logs by Criminal ID (criminal_id=1)`
   * `Get One Hunt Log by ID`
   * `Record Capture Attempt (POST - 201 Created)`
   * `Update Hunt Log (PATCH - 200 OK)`
   * `Delete Hunt Log (DELETE - 204 No Content)`
   * `[Invalid Request] Record Hunt with Non-Existent Criminal (404)`
   * `[Invalid Request] Get Non-Existent Hunt Log (404)`

### How to Import:
1. Open Postman.
2. Click **Import** (top left).
3. Drag & drop [`space_bounty_hunters.postman_collection.json`](space_bounty_hunters.postman_collection.json).
4. Variable `baseUrl` defaults to `http://localhost:8000`.

---

## 🧪 Running Automated Tests

A comprehensive suite of automated tests verifying all endpoints, queries, filters, validations, and status codes is included:

```bash
# Run pytest with verbose output
pytest -v
```

All tests run using an in-memory test database, guaranteeing fast, zero-dependency validation.
