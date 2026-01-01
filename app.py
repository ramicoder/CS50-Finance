import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    rows = db.execute(
    "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
    cash_balance = db.execute("SELECT cash FROM users WHERE id = (?)", user_id)[0]["cash"]
    total_owned = cash_balance

    for row in rows:
        row["price"] = lookup(row["symbol"])["price"]
        row["totalValue"] = row["shares"] * row["price"]
        total_owned = total_owned + row["totalValue"]

    return render_template("index.html", stocks=rows, balance=cash_balance, total=total_owned)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")

        if lookup(symbol) == None:
            return apology("invalid stock symbol")

        if not shares:
            return apology("must provide shares")

        if not shares.isdigit():
            return apology("invalid value of share")

        shares = int(shares)
        if shares <= 0:
            return apology("invalid value of share")

        user_id = session["user_id"]
        currentCash = db.execute("SELECT cash FROM users WHERE id = (?)", user_id)[0]["cash"]
        price = lookup(symbol)["price"]

        if price * shares <= currentCash:
            cost = shares * price

            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", cost, user_id)
            db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, ?)",
                       user_id, symbol, shares, price, 'Purchase')

            return redirect("/")
        else:
            return apology("insufficient amount of cash")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user_id = session["user_id"]
    rows = db.execute(
        "SELECT symbol, transaction_type, shares, datetime, price FROM transactions WHERE user_id = (?)", user_id)

    for row in rows:
        row["transaction_price"] = row["price"] * row["shares"]

    return render_template("history.html", transactions=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/verification", methods=["GET", "POST"])
def verification():
    if request.method == "POST":

        username = request.form.get("username")
        phrase = request.form.get("phrase")

        if not username:
            return apology("missing username")
        if not phrase:
            return apology("missing secret phrase")
        if phrase != db.execute("SELECT phrase FROM users WHERE username = (?)", username)[0]["phrase"]:
            return apology("wrong secret phrase")

        session["reset_user"] = username
        return redirect("/change")

    return render_template("verification.html")


@app.route("/change", methods=["GET", "POST"])
def change():

    if request.method == "POST":
        user = session.get("reset_user")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            return apology("missing password")
        if password == db.execute("SELECT hash FROM users WHERE username = (?)", user)[0]["hash"]:
            return apology("Cannot change it to previous password")
        if not confirmation:
            return apology("missing confirmation password")
        if password != confirmation:
            return apology("passwords do not match")

        newPass = generate_password_hash(password)
        db.execute("UPDATE users SET hash = (?) WHERE username = ?", newPass, user)
        return redirect("/")
    return render_template("change.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        stock = lookup(symbol)

        if stock is not None:
            user_id = session["user_id"]
            username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

            return render_template("quoted.html", username=username, name=stock["name"], price=stock["price"], symbol=stock["symbol"])
        else:
            return apology("invalid stock symbol")

    return render_template("quote.html", symbols=[symbol["symbol"] for symbol in db.execute("SELECT symbol FROM transactions")])


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        phrase = request.form.get("phrase")

        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if not confirmation:
            return apology("missing password confirmation")
        if not phrase:
            return apology("missing secret phrase")
        if password != confirmation:
            return apology("passwords do not match")
        try:
            db.execute("INSERT INTO users (username, hash, phrase) VALUES (?, ?, ?)",
                       username,
                       generate_password_hash(password),
                        phrase)
        except ValueError:
            return apology("username already exists")

        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = user_id

        return redirect("/")

    return render_template("register.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        user_id = session["user_id"]
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        symbolExist = lookup(symbol)

        if not symbol:
            return apology("must provide symbol")

        if symbolExist == None:
            return apology("invalid stock symbol")

        if not shares:
            return apology("must provide shares")

        if not shares.isdigit():
            return apology("invalid value of share")

        shares = int(shares)

        if shares <= 0:
            return apology("invalid value of share")

        stockOwned = db.execute(
            "SELECT symbol FROM transactions WHERE symbol = (?) AND user_id = (?)", symbol, user_id)

        if not stockOwned:
            return apology("stock not owned")

        shares_owned = db.execute(
            "SELECT SUM(shares) AS totalShares FROM transactions WHERE user_id = (?) AND symbol = (?)", user_id, symbol)[0]["totalShares"]

        if shares > shares_owned:
            return apology("insufficient shares amount")

        sale_value = symbolExist["price"] * shares

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", sale_value, user_id)
        return redirect("/")

    return render_template("sell.html", symbols=[symbol["symbol"] for symbol in db.execute("SELECT symbol FROM transactions")])
