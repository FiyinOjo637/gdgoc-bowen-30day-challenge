# To-Do App API

GDGoC Bowen 30-Day Challenge Capstone Project

## Live URL
https://gdgoc-bowen-todo.onrender.com

## Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | / | API info | No |
| POST | /auth/signup | Register user | No |
| POST | /auth/login | Login & get token | No |
| GET | /tasks | Get all tasks | Yes |
| POST | /tasks | Create task | Yes |
| PUT | /tasks/:id | Update task | Yes |
| DELETE | /tasks/:id | Delete task | Yes |

## Tech Stack
- FastAPI
- SQLAlchemy + SQLite
- JWT Authentication
- Bcrypt password hashing
- Deployed on Render