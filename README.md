# FastAPI Student CRUD API

A small FastAPI application for managing student records. It provides CRUD
operations plus filtering, sorting, and pagination. Records are stored in the
local `student.json` file; the application does not use a database.

## Project files

- `main.py` — FastAPI application, request models, validation, and endpoints.
- `student.json` — JSON file containing the student records used by the API.

## Requirements

- Python 3.10 or newer
- FastAPI, Uvicorn, and Pydantic 2 with its email validation dependency

## Setup and run

From the project directory, create and activate a virtual environment, install
the dependencies, and start the development server:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn "pydantic[email]>=2"
uvicorn main:app --reload
```

Run Uvicorn from the project directory so the app can find `student.json`.
When the server is running:

- API base URL: <http://127.0.0.1:8000>
- Interactive Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Student data

Each record is keyed by a string student ID in `student.json`. A student has:

| Field | Type | Rules |
| --- | --- | --- |
| `id` | string | Required for creation; unique among existing IDs |
| `name` | string | 2–50 characters; letters and spaces only |
| `age` | integer | Greater than 0 and less than 100 |
| `email` | string | Must be a valid email address |
| `gender` | string | One of `male`, `female`, or `others` |
| `course` | string or null | Optional |
| `year` | integer or null | Optional; greater than 0 and less than 5 |
| `gpa` | number or null | Optional; greater than 0 and at most 10 |
| `subjects` | list of strings or null | Optional |
| `address` | object or null | Optional; contains `city`, `state`, `country`, and `pincode` strings |
| `grade` | string or null | Computed from `gpa` in API responses; not stored in the JSON file |

Names are title-cased after validation. The computed grade is `A+` for GPA
9.0+, `A` for 8.0+, `B+` for 7.0+, `B` for 6.0+, `C` for 5.0+, and `F` below
5.0. If GPA is omitted, grade is `null`.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Returns a greeting. |
| `GET` | `/student` | Returns all students. |
| `GET` | `/student/{student_id}` | Returns one student by ID. |
| `GET` | `/filter?subject=Python` | Returns students taking the specified subject. If `subject` is omitted, returns all students. |
| `GET` | `/sort?sort_by=gpa&order=desc` | Sorts students by `gpa`, `age`, or `name`, in `asc` or `desc` order. |
| `GET` | `/paginate?page=1&limit=2` | Returns a page of students. `page` defaults to 1; `limit` defaults to 2 and must be between 1 and 100. |
| `POST` | `/create` | Creates a student; responds with `201 Created`. |
| `PUT` | `/update/{student_id}` | Updates the supplied fields for an existing student. |
| `DELETE` | `/delete/{student_id}` | Deletes a student by ID. |

### Example create request

Send a JSON body to `POST /create`:

```json
{
  "id": "5",
  "name": "Jordan Lee",
  "age": 20,
  "email": "jordan.lee@example.com",
  "gender": "others",
  "course": "Computer Science",
  "year": 2,
  "gpa": 8.4,
  "subjects": ["Python", "Databases"],
  "address": {
    "city": "Delhi",
    "state": "Delhi",
    "country": "India",
    "pincode": "110001"
  }
}
```

Optional fields may be omitted or set to `null`. The ID is required and must
not already exist. For updates, send only the fields to change in the body to
`PUT /update/{student_id}`.

## Responses and errors

- Student lookup, update, and delete return `404 Not Found` when the ID does
  not exist.
- Creation returns `409 Conflict` if the ID already exists.
- Invalid request data is rejected by FastAPI/Pydantic with a validation
  error response.
- Unsupported sort fields or sort orders are rejected with `404`.
- Pagination returns `404` when `page * limit` is greater than the number of
  students currently in the data file.

## Data storage notes

Changes made through create, update, and delete are written directly to
`student.json`. Keep a backup if the data matters. This file-based storage is
intended for a small example and does not provide database transactions or
concurrent-write protection.

Gender values are case-sensitive and must be lowercase when creating or
updating a record. Some sample records in the supplied JSON use capitalized
gender values; use the documented lowercase values for writes.
