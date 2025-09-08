# FastAPI Excel Processor

A tiny REST API that:
- creates categories,
- uploads Excel files into categories,
- parses all cell values (floats → `cells.float_value`, strings → `cells.str_value`),
- provides stats (`sum_type`) and search (`find_regions`).

Tech: **FastAPI**, **Poetry**, **SQLAlchemy 2.0**, **PostgreSQL (Docker)**, **pandas**.

---


## Installation & Running

### 1) Prerequisites
- **Docker** & **Docker Compose**
- **Python 3.11+**
- **Poetry** (`pipx install poetry` or `pip install --user poetry`)


### 2) Create .env file
Example:
  ```env
    API_PORT=8010

    POSTGRES_USER=root
    POSTGRES_PASSWORD=password
    POSTGRES_DB=excel_parser
    POSTGRES_PORT=54321
  ```


### 3) Start PostgreSQL (Docker)
- update docker-compose.yml if required
- Run:
```bash
docker compose up -d
```

### 4) Install Python dependencies using Poetry
```bash
poetry install
```

### 5) Initialize the database schema from tables.sql

  ```bash
  docker cp tables.sql postgres_excel_parser:/tmp/tables.sql
  docker exec -it postgres_excel_parser psql -U root -d excel_parser -f /tmp/tables.sql
  ```

### 6) Run the API via `main.py`
Run:
```bash
poetry run python main.py
```
Open docs: <http://127.0.0.1:8010/docs>

---

## Endpoint Quickstart

Create a category:
```bash
curl -X POST http://127.0.0.1:8010/create_category   -H "Content-Type: application/json"   -d '{"category_name":"Sales","region":"IL","type":"monthly"}'
```

Upload an Excel file:
```bash
curl -X POST "http://127.0.0.1:8010/upload_file?category_name=Sales"   -F "file=@sample.xlsx"
```

Sum by type:
```bash
curl "http://127.0.0.1:8010/sum_type?type=monthly"
```

Find regions by search term (case-insensitive):
```bash
curl "http://127.0.0.1:8010/find_regions?search_term=Revenue"
```

---

## Case-Insensitive Search & Trigram Optimization

- `find_regions` uses **case-insensitive** matching (`ILIKE`) on `cells.str_value` (text)

  This significantly accelerates substring searches on large `cells` tables.

---

## Project Structure

```
fastapi-excel-parser/
├─ src/
│  ├─ controller.py        # FastAPI app & endpoints
│  ├─ models.py            # SQLAlchemy models (categories, files, cells)
│  ├─ repository.py        # CategoryRepository, FileRepository, CellRepository
│  ├─ db.py                # engine + SessionLocal
├─ main.py                 # uvicorn runner
├─ tables.sql              # SQL incl. pg_trgm + trigram index
├─ pyproject.toml
├─ docker-compose.yml
└─ README.md
```
