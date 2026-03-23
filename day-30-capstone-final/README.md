# To-Do App API 📝

> GDGoC Bowen 30-Day Challenge — Capstone Project
> Built by Fiyinfoluwa Ojo | Backend Development Track

## 🌍 Live URL
https://gdgoc-bowen-todo.onrender.com

## 📖 API Documentation
https://gdgoc-bowen-todo.onrender.com/docs

## 🚀 Features
- JWT Authentication (signup & login)
- Full CRUD task management
- Task priority levels (low, medium, high)
- Filter by priority and completion status
- Pagination with metadata
- Input validation with Pydantic
- Global error handling
- CORS enabled for frontend integration
- Fully documented with Swagger UI

## 🛠 Tech Stack
- **Framework:** FastAPI (Python)
- **Database:** SQLite + SQLAlchemy ORM
- **Auth:** JWT + Bcrypt password hashing
- **Validation:** Pydantic
- **Deployment:** Render
- **Testing:** Pytest (10 tests passing)

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/signup | Register new user |
| POST | /auth/login | Login & get JWT token |

### Tasks (🔒 Requires Bearer Token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tasks | Get all tasks (with filters) |
| POST | /tasks | Create new task |
| PUT | /tasks/:id | Update task |
| DELETE | /tasks/:id | Delete task |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API info |
| GET | /status | Health check |

## 🔍 Query Parameters
- `?page=1&limit=10` → pagination
- `?priority=high` → filter by priority
- `?completed=false` → filter by status
- `?priority=high&completed=false` → combined

## ⚡ Quick Start

### 1. Signup
```
POST /auth/signup
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 2. Login
```
POST /auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 3. Create Task
```
POST /tasks
Authorization: Bearer <token>
{
  "title": "My first task",
  "description": "Get things done",
  "priority": "high"
}
```

### 4. Get Tasks
```
GET /tasks?priority=high&completed=false
Authorization: Bearer <token>
```

## 🧪 Running Tests
pip install pytest httpx
pytest tests/ -v

## 📁 Project Structure
gdgoc-bowen-30day-challenge/
├── day-01-http-fundamentals/
├── day-02-restful-routes/
├── day-03-git-environment/
├── ...
├── day-29-capstone-polish/
└── day-30-capstone-final/  ← You are here

## 👨‍💻 Developer
**Fiyinfoluwa Ojo**
- Dev.to: https://dev.to/ghost_script
- GitHub: https://github.com/FiyinOjo637