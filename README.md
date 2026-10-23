# SpendWise — Personal Expense Tracker & Analytics

A Flask application for recording income and expenses, filtering transactions, viewing monthly/category charts, and exporting CSV reports.

## Stack
Python, Flask, Flask-SQLAlchemy, SQLite by default, Pandas, Matplotlib, HTML/CSS. Optional MySQL schema included.

## Run in VS Code (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```
Open http://127.0.0.1:5000. The database is created automatically.

If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
If `python` is not recognized but `py` works, use `py` instead of `python`.

## Folder structure
```text
personal-expense-tracker/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── schema.sql
├── README.md
├── sample_data/
│   └── sample_transactions.csv
├── static/style.css
└── templates/
    ├── base.html
    ├── dashboard.html
    └── add.html
```

## GitHub
Create an empty repository named `personal-expense-tracker`, then run:
```powershell
git init
git add .
git status
git commit -m "Build personal expense tracker and analytics"
git branch -M main
git remote add origin https://github.com/geetaharinic/personal-expense-tracker.git
git push -u origin main
```
Check `git status` before committing. Never commit `.env`, `.venv`, database files, or private financial data. Configure Git identity if needed with `git config --global user.name "Geeta Harini"` and `git config --global user.email "YOUR-GITHUB-EMAIL"`.

## Notes
Amounts are treated as INR (₹). The app has no authentication and is intended for local learning; do not expose it publicly with real personal financial records. It reports descriptive totals, not financial advice.
