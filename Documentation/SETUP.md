# System Setup & Deployment Guide

This guide details how to configure, deploy, and run the E-commerce Platform backend and database.

---

## Prerequisites

Ensure you have the following software installed on your system:
- **MariaDB** or **MySQL** server (Port `3306`)
- **Python 3.10+**
- **pip** (Python package installer)

---

## 1. Database Setup

To set up the database schema, roles, and populate seed data:

1. Connect to your MariaDB instance using your preferred client (e.g. MySQL Workbench, terminal):
   ```bash
   mariadb -u root -p
   ```
2. Run the SQL scripts located inside the `Database/` folder in the following **exact order**:
   ```sql
   SOURCE Database/create_database.sql;
   SOURCE Database/create_tables.sql;
   SOURCE Database/insert_data.sql;
   SOURCE Database/views.sql;
   SOURCE Database/procedures.sql;
   SOURCE Database/triggers.sql;
   ```

*(Note: If running scripts via a GUI client like MySQL Workbench, open and execute each file sequentially).*

---

## 2. Backend Environment Configuration

1. Create a Python Virtual Environment:
   ```bash
   python3 -m venv .venv
   ```
2. Activate the virtual environment:
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```cmd
     .venv\Scripts\activate
     ```
3. Install required Python packages:
   ```bash
   pip install flask flask-cors mariadb python-dotenv PyJWT bcrypt
   ```
4. Create your local environment file:
   - Create a file named `.env` inside `Application/configuration files/`.
   - Add the following configurations, ensuring you replace the placeholder values with your MariaDB database settings:
     ```env
     MARIA_DB_PASS='your_database_password_here'
     SECRET_KEY='choose_any_jwt_secret_key'
     MARIA_DB_USER='your_username' # E.g., 'root' or 'harisissah'
     MARIA_DB_HOST='localhost'
     MARIA_DB_PORT=3306
     MARIA_DB_DB='ecommerce'
     ```

---

## 3. Launching the Backend Server

Start the development Flask server from the source code directory:

```bash
cd "Application/source code"
python api/app.py
```

*The Flask server will launch on `http://127.0.0.1:5001`. Keep this terminal window open.*

---

## 4. Serving the Frontend

Since the frontend is a client-side web application built with HTML/CSS/JS:

1. Open the [Application/source code/frontend/](file:///Users/harisissah/Documents/Ashesi/db%20assignments/final_project_database/Application/source%20code/frontend/) directory.
2. Launch `login.html` or `products/products.html` in your web browser.
   - For the best experience (avoiding CORS caching issues), serve the frontend using a lightweight server, such as the VS Code **Live Server** extension (typically runs on `http://127.0.0.1:5500/`).
3. You can authenticate and sign in using the seed stakeholder profiles documented in the root [README.md](file:///Users/harisissah/Documents/Ashesi/db%20assignments/final_project_database/README.md).
