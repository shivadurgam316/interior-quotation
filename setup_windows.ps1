$ErrorActionPreference = "Stop"

Write-Host "Interior Quotation - Windows setup"
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python was not found. Install Python 3.11+ first."
    exit 1
}

if (-not (Test-Path ".\venv")) {
    python -m venv venv
}

& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env created. Edit DB_PASSWORD and other database settings."
}

Write-Host ""
Write-Host "Next:"
Write-Host "1. Create MySQL database 'interior_quotation' in HeidiSQL."
Write-Host "2. Edit .env with your MySQL credentials."
Write-Host "3. Run: .\venv\Scripts\python.exe manage.py migrate"
Write-Host "4. Run the schema.sql file in HeidiSQL."
Write-Host "5. Run: .\venv\Scripts\python.exe manage.py createsuperuser"
Write-Host "6. Run: .\venv\Scripts\python.exe manage.py runserver"
