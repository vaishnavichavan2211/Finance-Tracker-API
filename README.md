 💰 Finance Tracker API 

This is a simple **Finance Tracker API** built using **FastAPI**, **MySQL**,
It allows users to manage their income and expenses with authentication and role-based access.

---

##  Features

*  JWT Authentication (Login with token)
*  User roles: Admin, Analyst, Viewer
*  Add, update, delete financial records
*  Filter records by date, category, type
*  Basic analytics (income, expenses, balance)
*  Pagination support
*  Input validation using Pydantic
*  Auto API docs using Swagger

---

## Project Structure

```
finance_tracker/
├── app/
│   ├── main.py
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── routers/
├── scripts/
├── .env.example
├── requirements.txt
└── README.md
```

---

##  Requirements

* Python 3.9+
* MySQL installed

---

## Setup Instructions

### 1. Clone the project

```bash
git clone <your-repo-url>
cd finance_tracker
```

---

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create MySQL Database

```sql
CREATE DATABASE finance_tracker;
```

---

### 5. Setup environment variables

Copy file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=finance_tracker
SECRET_KEY=your-secret-key
```

---

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

Open in browser:

```
http://localhost:8000/docs
```

---

### 7. (Optional) Add sample data

```bash
python scripts/seed_data.py
```

Sample users:

| Role    | Email                                         | Password   |
| ------- | --------------------------------------------- | ---------- |
| Admin   | [alice@example.com](mailto:alice@example.com) | admin123   |
| Analyst | [bob@example.com](mailto:bob@example.com)     | analyst123 |
| Viewer  | [carol@example.com](mailto:carol@example.com) | viewer123  |

---

##  Authentication

### Login

```bash
POST /api/v1/auth/login
```

### Use Token

```bash
Authorization: Bearer <your_token>
```

---

##  API Endpoints

### Auth

* POST `/auth/login`

### Users

* POST `/users/register`
* GET `/users/me`

### Records

* POST `/records/`
* GET `/records/`
* PUT `/records/{id}`
* DELETE `/records/{id}`

### Analytics

* GET `/analytics/summary`
* GET `/analytics/monthly`

---

##  Roles

| Action    | Viewer | Analyst | Admin |
| --------- | ------ | ------- | ----- |
| View data | ✅      | ✅       | ✅     |
| Add/Edit  | ❌      | ✅       | ✅     |
| Delete    | ❌      | ❌       | ✅     |
| Analytics | ❌      | ✅       | ✅     |

---

## API Docs

* Swagger UI → http://localhost:8000/docs
* ReDoc → http://localhost:8000/redoc

---

##  Conclusion

This is a beginner-friendly backend project to practice:

* API development
* Authentication
* Database handling
* Clean project structure

