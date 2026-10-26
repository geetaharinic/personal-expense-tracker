import os
from datetime import date, datetime
from io import BytesIO
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")
database_url = os.getenv("DATABASE_URL", "sqlite:///expenses.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
CATEGORIES = ["Food", "Transport", "Education", "Shopping", "Bills", "Health", "Entertainment", "Other"]

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), nullable=False, default="Other")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

def chart(labels, values, title, ylabel, bars=False):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    if not labels:
        ax.text(.5, .5, "Add transactions to see charts", ha="center", va="center")
        ax.set_axis_off()
    elif bars:
        ax.bar(labels, values)
        ax.tick_params(axis="x", labelrotation=25)
    else:
        ax.plot(labels, values, marker="o")
        ax.tick_params(axis="x", labelrotation=25)
    ax.set_title(title); ax.set_ylabel(ylabel); ax.grid(axis="y", alpha=.2); fig.tight_layout()
    out = BytesIO(); fig.savefig(out, format="png", dpi=120); plt.close(fig)
    return base64.b64encode(out.getvalue()).decode()

@app.route("/")
def dashboard():
    start, end = request.args.get("start_date", ""), request.args.get("end_date", "")
    category, kind = request.args.get("category", ""), request.args.get("type", "")
    q = Transaction.query
    try:
        if start: q = q.filter(Transaction.transaction_date >= date.fromisoformat(start))
        if end: q = q.filter(Transaction.transaction_date <= date.fromisoformat(end))
    except ValueError:
        flash("Invalid date filter.", "error"); start = end = ""
    if category in CATEGORIES: q = q.filter_by(category=category)
    if kind in ("income", "expense"): q = q.filter_by(transaction_type=kind)
    rows = q.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).all()
    income = sum(t.amount for t in rows if t.transaction_type == "income")
    expenses = sum(t.amount for t in rows if t.transaction_type == "expense")
    monthly, cats = {}, {}
    for t in rows:
        if t.transaction_type == "expense":
            key = t.transaction_date.strftime("%Y-%m")
            monthly[key] = monthly.get(key, 0) + t.amount
            cats[t.category] = cats.get(t.category, 0) + t.amount
    return render_template("dashboard.html", rows=rows, categories=CATEGORIES, start=start, end=end,
        category=category, kind=kind, income=income, expenses=expenses, balance=income-expenses,
        monthly_chart=chart(sorted(monthly), [monthly[k] for k in sorted(monthly)], "Monthly expenses", "₹"),
        category_chart=chart(list(cats), list(cats.values()), "Expenses by category", "₹", True))

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            dt = date.fromisoformat(request.form["transaction_date"])
            kind, category = request.form["transaction_type"], request.form["category"]
            description = request.form["description"].strip()
            amount = float(request.form["amount"])
            method = request.form["payment_method"]
            if kind not in ("income", "expense") or category not in CATEGORIES: raise ValueError("Choose a valid type and category.")
            if not description or len(description) > 200: raise ValueError("Description is required (maximum 200 characters).")
            if amount <= 0: raise ValueError("Amount must be greater than zero.")
            if method not in ("Cash", "UPI", "Card", "Bank Transfer", "Other"): raise ValueError("Choose a valid payment method.")
            db.session.add(Transaction(transaction_date=dt, transaction_type=kind, category=category,
                description=description, amount=amount, payment_method=method))
            db.session.commit(); flash("Transaction added.", "success"); return redirect(url_for("dashboard"))
        except (ValueError, KeyError) as e:
            flash(str(e) or "Check the form values.", "error")
    return render_template("add.html", categories=CATEGORIES, today=date.today().isoformat())

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = db.session.get(Transaction, item_id)
    if item:
        db.session.delete(item); db.session.commit(); flash("Transaction deleted.", "success")
    else: flash("Transaction not found.", "error")
    return redirect(url_for("dashboard"))

@app.route("/export")
def export():
    rows = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    data = [{"date":t.transaction_date.isoformat(),"type":t.transaction_type,"category":t.category,
        "description":t.description,"amount":t.amount,"payment_method":t.payment_method} for t in rows]
    buf = BytesIO(); pd.DataFrame(data, columns=["date","type","category","description","amount","payment_method"]).to_csv(buf,index=False)
    buf.seek(0)
    return send_file(buf, mimetype="text/csv", as_attachment=True, download_name="expense_transactions.csv")

with app.app_context(): db.create_all()
if __name__ == "__main__": app.run(debug=os.getenv("FLASK_DEBUG","false").lower()=="true")
