# E-commerce Platform

### Project Members
- Gabriel Kwesi Takyi Akurang
- Ewurakua Amoah
- Haris Tiyumtaba Issah
- Emmanuel Kwesi Bentsil Odoom

### Tech Stack
- **Database**: MariaDB / MySQL
- **Backend API**: Python (Flask)
- **Frontend**: HTML, CSS, JavaScript (served via browser/Live Server)

---

## Directory Structure

```text
Project/
│
├── Documentation/
│   ├── DESIGN.md
│   └── README_CHANGES.md
│
├── Database/
│   ├── create_database.sql
│   ├── create_tables.sql
│   ├── insert_data.sql
│   ├── queries.sql
│   ├── views.sql
│   ├── procedures.sql
│   └── triggers.sql
│
├── Application/
│   ├── source code/
│   │   ├── api/
│   │   ├── database/
│   │   ├── model/
│   │   ├── service/
│   │   ├── frontend/
│   │   └── auth.py
│   └── configuration files/
│       ├── .env
│       └── .gitignore
│
├── Screenshots/
│
├── Video/
│   └── project_demo.mp4
│
└── README.md
```

---

## Getting Started

### 1. Database Setup Order
To recreate the database locally, execute the SQL files inside the `Database/` directory in this exact order:
1. `create_database.sql` (Creates and selects the database schema)
2. `create_tables.sql` (Creates all tables, constraints, roles, and privileges)
3. `insert_data.sql` (Inserts mock seed data with pre-hashed passwords)
4. `views.sql` (Creates all reporting and analytics views)
5. `procedures.sql` (Creates custom stored functions and procedures)
6. `triggers.sql` (Registers database event triggers)

*Note: For testing, sample database queries can be found in `queries.sql`.*

### 2. Initial Stakeholders (Emails & Passwords)
Use the following credentials to access the platform:

**Vendors** (Password: **`vendor123`**):
- `info@vndr01.com` to `info@vndr05.com`

**Admin**:
- Username: **`admin`**
- Password: **`admin`**

**Customers & Shipping Companies** (Password: **`password123`**):
- Customers: `kofi.mensah1@email.com`, `ama.asante2@email.com`, etc.
- Shipping: `speedy@shipping.gh`, `dhl@shipping.gh`, etc.

### 3. Setting up the `.env` File
Ensure your `.env` file is located inside `Application/configuration files/` with the following configuration:

```env
MARIA_DB_PASS='your_database_password_here'
SECRET_KEY='any_secret_key_of_choice'
MARIA_DB_USER='your_username_here' # e.g. root or harisissah
```

### 4. Running the Backend Server
To run the Flask application, navigate into the source directory and run `app.py`:

```bash
cd "Application/source code"
python api/app.py
```

This starts the development server on `http://127.0.0.1:5001`. The frontend static pages can then be launched (e.g. using Live Server or direct browser loading).
