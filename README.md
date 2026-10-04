# Interior Quotation - Django + MySQL/MariaDB + Direct SQL

This project intentionally does NOT use Django models for the quotation business tables.

- Django handles the web application and authentication.
- MySQL/MariaDB is the database.
- HeidiSQL is used to create/view/manage the database.
- Business tables are created by `quotations/sql/schema.sql`.
- Application database access uses direct SQL through `django.db.connection`.
- PDF generation uses ReportLab.
- Email is not implemented in V1.
- WhatsApp V1 uses a WhatsApp link with a prefilled message. Official WhatsApp Cloud API PDF delivery can be added after API credentials/template approval are available.

## Important: HeidiSQL

HeidiSQL is a database GUI/client. It is not the database server.

You need one of:
- MySQL Server
- MariaDB Server

running locally or on a remote server.

## Windows setup

### 1. Install Python

Install Python 3.11+ and make sure `python` works in PowerShell.

### 2. Install MySQL/MariaDB

Create a database in HeidiSQL by opening a query and running:

```sql
CREATE DATABASE interior_quotation
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Then select the database and run:

```text
quotations/sql/schema.sql
```

### 3. Create and activate virtual environment

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 4. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Set your MySQL credentials:

```text
DB_NAME=interior_quotation
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Create Django default tables

```powershell
python manage.py migrate
```

This creates Django's standard tables such as auth_user, auth_group, django_session, etc.

### 6. Create admin user

```powershell
python manage.py createsuperuser
```

### 7. Run server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## Application pages

```text
/                         Dashboard
/customers/               Customers
/customers/create/        Add customer
/products/                Products
/products/create/         Add product
/quotation/create/        Create quotation
/quotation/<id>/          Quotation preview
/quotation/<id>/pdf/      Download quotation PDF
```

## Database tables

Django default tables:
- auth_user
- auth_group
- auth_permission
- django_admin_log
- django_content_type
- django_migrations
- django_session

Application tables:
- quotation_company
- quotation_customer
- quotation_product
- quotation
- quotation_item
- quotation_delivery_log
- quotation_sequence

## Current quotation flow

```text
Customer
   |
   v
Create quotation
   |
   v
Add line items
   |
   v
Automatic subtotal/SGST/CGST/grand total
   |
   v
Save in MySQL
   |
   v
Preview quotation
   |
   v
Download PDF
   |
   v
Open WhatsApp with prefilled message
```

The current WhatsApp action intentionally opens WhatsApp. Automatic PDF sending through the official WhatsApp Business Cloud API requires a configured Meta business account, phone number, access token, media upload and approved messaging template where applicable. Those credentials should not be hard-coded into this project.
