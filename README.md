# TaskFlow — Team Task Manager

A full-stack web application for team project and task management with role-based access control (Admin/Member).

**Live URL:** _[Add after deployment]_

## Features

- **Authentication** — Signup/Login with JWT tokens
- **Project Management** — Create, update, delete projects with team collaboration
- **Task Tracking** — Kanban board with drag-and-drop status updates (To Do → In Progress → Done)
- **Role-Based Access Control** — Admin and Member roles with granular permissions
- **Team Management** — Add/remove members, assign tasks to team members
- **Dashboard** — Overview with task statistics, overdue alerts, and recent activity

## Tech Stack

| Layer | Technology |
|:---|:---|
| Backend | Python / Flask |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | JWT (flask-jwt-extended) |
| Frontend | Jinja2 Templates + Vanilla JS/CSS |
| Server | Gunicorn |
| Deployment | Railway |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|:---|:---|:---|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Get current user |

### Projects
| Method | Endpoint | Description |
|:---|:---|:---|
| GET | `/api/projects` | List user's projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/:id` | Get project details |
| PUT | `/api/projects/:id` | Update project (Admin) |
| DELETE | `/api/projects/:id` | Delete project (Admin) |
| POST | `/api/projects/:id/members` | Add member (Admin) |
| DELETE | `/api/projects/:id/members/:uid` | Remove member (Admin) |

### Tasks
| Method | Endpoint | Description |
|:---|:---|:---|
| GET | `/api/projects/:id/tasks` | List project tasks |
| POST | `/api/projects/:id/tasks` | Create task |
| PUT | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task (Admin) |
| PATCH | `/api/tasks/:id/status` | Update status |

### Dashboard
| Method | Endpoint | Description |
|:---|:---|:---|
| GET | `/api/dashboard` | Get dashboard stats |

## Role-Based Access

| Action | Admin | Member |
|:---|:---:|:---:|
| Create project | ✅ | ✅ |
| Edit/delete project | ✅ | ❌ |
| Add/remove members | ✅ | ❌ |
| Create tasks | ✅ | ✅ |
| Assign tasks | ✅ | ❌ |
| Update task status | ✅ | ✅ (if assigned) |
| Delete tasks | ✅ | ❌ |

## Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd Project

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app (uses SQLite locally)
flask --app app:create_app run --debug

# Open http://localhost:5000
```

## Railway Deployment

1. Push code to GitHub
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repository
4. Add a **PostgreSQL** database plugin
5. Set environment variables:
   - `JWT_SECRET_KEY` — a random secret string
   - `SECRET_KEY` — a random secret string
6. Railway auto-detects Python and deploys
7. Go to **Settings → Networking → Generate Domain**

## Project Structure

```
Project/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── routes/              # API & page routes
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   ├── dashboard.py
│   │   └── pages.py
│   ├── utils/               # Decorators & validators
│   ├── static/css/          # Stylesheets
│   ├── static/js/           # Frontend JavaScript
│   └── templates/           # Jinja2 HTML templates
├── requirements.txt
├── Procfile
└── README.md
```
