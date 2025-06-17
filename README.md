# 🚀 FastAPI Starter Template

A powerful and scalable FastAPI template built with real-world architecture in mind. This template comes with a fully integrated authentication service, background task processing using Celery, Redis, and Flower, custom email templates, PostgreSQL support, and complete test coverage using Pytest.

---

## ✨ Features

* 🔐 **Authentication**

  * JWT-based login & registration system
  * Password reset & email verification flow
  * OAuth2 ready structure

* ⏱ **Asynchronous Background Jobs**

  * Celery for task management
  * Redis as message broker
  * Flower for task monitoring

* 📜 **Custom Email Templates**

  * Jinja2 templating
  * HTML email support for all auth flows
  * Plug-and-play SMTP settings

* 👥 **Database**

  * PostgreSQL
  * SQLAlchemy + Alembic for ORM and migrations
  * Async session support

* 🧪 **Testing**

  * Pytest configured
  * Test coverage for auth, core, and tasks
  * Fixtures and test database isolation

* 🛠 **Dev Tools**

  * Pre-configured `.env` support
  * Auto reload with `uvicorn`

---

## 📁 Project Structure

```
.
├── src/
│   ├── config.py           # Configuration, settings, base classes
│   ├── auth/               # Auth routes, models, logic
│   ├── user/               # Users routes, models, logic
│   ├── tasks/              # Celery tasks (emails, notifications, etc.)
│   ├── templates/          # Email templates (HTML + Jinja2)
│   ├── db/                 # Database models and session setup
│   ├── tests/              # Unit and integration tests
│   ├── utils/              # Utility functions and helpers
│   ├── misc/               # Miscellaneous logic
│   └── __init__.py         # Entry point for FastAPI
├── tests/                  # Unit and integration tests
├── alembic.ini             # Migrations
├── requirements.txt
└── README.md
```

---

## 🧪 Running the Project

### 1. Clone the repo

```bash
git clone https://github.com/Theo-flux/fast-template.git
cd fastapi-template
```

### 2. Create your `.env` file

```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
JWT_SECRET=<secret>
JWT_ALGORITHM=<ALGORITHM>

REDIS_HOST=localhost
REDIS_PORT=6379

MAIL_USERNAME=<username>
MAIL_PASSWORD=<password>
MAIL_FROM=<gmail>
MAIL_PORT=465
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=<username>

EMAIL_SALT=<salt string>
```

* FastAPI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
* Flower: [http://localhost:5555](http://localhost:5555) (task monitor)

---

## 🔀 Running Background Tasks

Use Celery for background jobs like sending emails.

```bash
celery -A src.tasks worker --loglevel=info
```

To monitor tasks:

```bash
celery -A src.tasks flower --port=5555
```

---

## 🧪 Running Tests

```bash
pytest
```

Includes fixtures, isolated test DB, and mocking tools for background jobs and emails.

---

## 🧰 Tech Stack

* **FastAPI**
* **PostgreSQL**
* **Celery + Redis + Flower**
* **SQLAlchemy + Alembic**
* **Jinja2**
* **Pytest**

---

## 📬 Email Templates

Located in `src/templates/`. You can customize:

* Email verification
* Password reset
* Welcome emails

Rendered with Jinja2 and sent asynchronously via Celery.

---

## 📄 License

MIT License — feel free to fork and adapt for your own use.

---

## ✍️ Author

Created by [Theo-flux](https://github.com/Theo-flux)
