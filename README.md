<h3></h3>
E-commerce platform 


Gabriel Kwesi Takyi Akurang
Ewurakua Amoah
Haris Tiyumtaba Issah
Emmanuel Kwesi Bentsil Odoom

Maria DB, MySQL Workbench, VS Code, Python

Maria DB

Python programming language with the Flask framework

The application is web based hence installation won't be necessary. All that is required is the web URL. 

The database is already created and exists on a server. All one has to do to interact with it is to enter the web URL of the platform and to engage with the frontend interface.

The Database is populated when users provide query information on the frontend. Users with no clearance have no direct access to the database.

The application is run by starting the server and loading the frontend components. After this, an event loop that consists of the server consistently logging actions is spun. This makes the web service accessible via a localhost

## Getting Started (For Group Members)

### 1. Database Setup Order
To recreate the database locally on your device, execute the SQL files in your MariaDB instance in this exact order:
1. `new_ddl.sql` (Creates schemas and tables with UUID/VARCHAR(36) and activation flags support)
2. `new_dml.sql` (Inserts seeded mock data with pre-hashed bcrypt passwords)
3. `new_phase 6 and 7.sql` (Unified roles, privileges, views, stored procedures, functions, and triggers)

*(Note: The old files `ddl.sql`, `dml.sql`, and `phase 6 and 7.sql` represent initial stages. The obsolete migration files `Haris_changes*.sql` and `update_passwords.sql` have been removed as they are fully consolidated into the `new_*.sql` files).*


### 2. Initial Stakeholders (Emails & Passwords)
 You can use the following default credentials to access the platform:

**Vendors** (Password for all vendors is **`vendor123`**):
- `info@vndr01.com`
- `info@vndr02.com`
- `info@vndr03.com`
- `info@vndr04.com`
- `info@vndr05.com`

**Admin**:
- Email / Username: **`admin`**
- Password: **`admin`**

**Customers**:
- `kofi.mensah1@email.com`
- `ama.asante2@email.com`
- `john.doe3@email.com`
- `kwame.osei4@email.com`
- `esi.boakye5@email.com`

**Shipping Companies**:
- `speedy@shipping.gh`
- `ecotransit@shipping.gh`
- `dropx@shipping.gh`
- `aramex@shipping.gh`
- `dhl@shipping.gh`

*(Password for all Customers & Shipping Companies is **`password123`**)*

### 3. Modifying `database.py`
To connect the application to your local database, you need to open `database.py` and modify the `user` property inside the `connect()` function (around line 10) to match your MariaDB username.
```python
def connect():
    return mariadb.connect(
        host="localhost",
        user="root", # Change 'harisissah' to your own MariaDB username (e.g. 'root')
        password=os.getenv("MARIA_DB_PASS"),
        database="ecommerce",
        port=3306
    )
```

### 4. Setting up the `.env` File
Create a new file named `.env` in the root folder of the project (next to `database.py`) and add the following lines. Make sure to replace the `MARIA_DB_PASS` value with your actual MariaDB password. Also, you can change the secret key to whatever you want:

```env
MARIA_DB_PASS='your_database_password_here'
SECRET_KEY='any_secret_key_of_choice'
```
