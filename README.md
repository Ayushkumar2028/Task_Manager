Live Link https://taskmanager-frontend-5338.onrender.com/login
# Full-Stack Task Manager (Django + React)

A complete full-stack web application built for managing tasks with Role-Based Access Control (RBAC).

## Features

- **Backend**: Django & Django REST Framework (DRF)
- **Frontend**: React (Vite)
- **Database**: SQLite (configured for easy switch to PostgreSQL)
- **Authentication**: JWT (JSON Web Tokens)
- **Role Management**: Admin vs User roles using Django Groups
- **Design Aesthetic**: Premium glassmorphism, vibrant dark mode, micro-animations
- **Complete CRUD Module**: Create, read, update, delete tasks.
- **API Documentation**: Generated via Swagger (DRF-YASG).

---

## 🛠 Prerequisites

- Python 3.10+
- Node.js 18+

---

## 🚀 Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # For Windows
# source venv/bin/activate # For macOS/Linux

pip install -r requirements.txt
```

**(Note: If there is no `requirements.txt`, install manually based on the script: `pip install django djangorestframework djangorestframework-simplejwt django-cors-headers drf-yasg python-dotenv Pillow`)**

Apply Migrations and load initial data:

```bash
python manage.py makemigrations accounts tasks
python manage.py migrate
python manage.py create_initial_data
```

This populates default Admin and User groups and creates a superuser:
- **Username**: `admin`
- **Password**: `Admin@123`

Start the server:
```bash
python manage.py runserver
```
*API Base URL: http://localhost:8000/api/v1/*
*Swagger Docs: http://localhost:8000/swagger/*
*Django Admin: http://localhost:8000/admin/*

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

*The App runs on http://localhost:5173 (or as specified by Vite)*

---

## 📖 API Endpoint Documentation (v1)

### Auth Endpoints
- `POST /api/v1/auth/register/` - Register a new user
- `POST /api/v1/auth/login/` - Login & get JWT token (Access + Refresh)
- `POST /api/v1/auth/logout/` - Blacklist refresh token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT
- `GET /api/v1/auth/profile/` - Get current user profile
- `PATCH /api/v1/auth/profile/` - Update profile

### Tasks Endpoints
- `GET /api/v1/tasks/` - List tasks (Filtered by User, Admins see all)
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{id}/` - Get single task info
- `PATCH /api/v1/tasks/{id}/` - Partially update task
- `DELETE /api/v1/tasks/{id}/` - Delete task
- `GET /api/v1/tasks/stats/` - Status/Priority counts

### Example Request (Login)
```json
POST /api/v1/auth/login/
{
  "username": "admin",
  "password": "Admin@123"
}
```

### Example Request (Create Task)
```json
POST /api/v1/tasks/
Headers: { "Authorization": "Bearer <ACCESS_TOKEN>" }
{
  "title": "Complete Assignment",
  "description": "Finish the Django React task",
  "status": "pending",
  "priority": "urgent"
}
```


