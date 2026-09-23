# CRC Assessment 2 — FastAPI Practical

Two fully working FastAPI applications built with **SQLite** and **SQLModel**.

---

## Projects

| Task | Folder | Port |
|------|--------|------|
| Task 1 — Campus Lost & Found API | `task1_lost_found/` | 8000 |
| Task 2 — Campus Event Reservation API | `task2_event_reservation/` | 8001 |

---

## Requirements

- Python 3.10+
- pip

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ujjwalbhar/CRC-Assessment-2.git
cd CRC-Assessment-2

# 2. Create and activate a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Applications

### Task 1 — Lost & Found API

```bash
cd task1_lost_found
uvicorn main:app --reload --port 8000
```

Swagger UI → http://127.0.0.1:8000/docs

### Task 2 — Event Reservation API

```bash
cd task2_event_reservation
uvicorn main:app --reload --port 8001
```

Swagger UI → http://127.0.0.1:8001/docs

---

## Task 1 — API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/items` | Report a new lost/found item |
| GET | `/items` | Get all reported items |
| GET | `/items/{item_id}` | Get a specific item by ID |
| PUT | `/items/{item_id}` | Update item details or status |
| DELETE | `/items/{item_id}` | Delete an item report |
| GET | `/items/status/{status}` | Filter items by status (Lost/Found/Returned) |
| GET | `/items/category/{category}` | Filter items by category |

### Sample POST `/items` body

```json
{
  "title": "Black Wallet",
  "description": "Black leather wallet with student ID inside",
  "category": "Accessories",
  "location": "Library - 2nd Floor",
  "reported_by": "Rahul Sharma",
  "status": "Lost"
}
```

---

## Task 2 — API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/events` | Create a new event |
| GET | `/events` | Get all events |
| GET | `/events/{event_id}` | Get a specific event |
| PUT | `/events/{event_id}` | Update event details |
| DELETE | `/events/{event_id}` | Delete an event |
| POST | `/events/{event_id}/reserve` | Reserve a seat for an event |
| GET | `/events/{event_id}/reservations` | Get all reservations for an event |
| DELETE | `/reservations/{reservation_id}` | Cancel a reservation |
| GET | `/events/{event_id}/availability` | Check seat availability |

### Sample POST `/events` body

```json
{
  "title": "Python Workshop",
  "venue": "CS Lab 101",
  "capacity": 30,
  "organizer": "Computer Science Dept",
  "status": "Open"
}
```

### Sample POST `/events/{event_id}/reserve` body

```json
{
  "student_name": "Priya Patel",
  "roll_number": "CS2023045",
  "email": "priya@college.edu"
}
```

---

## Screenshots

Screenshots proving successful API execution are located in the `screenshots/` folder.

---

## Tech Stack

- **FastAPI** — Web framework
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic)
- **SQLite** — Database
- **Uvicorn** — ASGI server
- **Pydantic** — Data validation
