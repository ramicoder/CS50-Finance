# C$50 Finance

A web-based stock trading simulation implemented as the final problem set for the **CS50: Introduction to Computer Science** "Web Track".

## 🚀 Project Overview
C$50 Finance is a web application that allows users to manage a virtual stock portfolio. Users can create an account, check real-time stock prices, "buy" and "sell" stocks using virtual cash, and view their transaction history.

## 🔑 Key Features
* **Authentication:** Secure user registration, login, and logout.
* **Quote:** Look up real-time stock prices using the IEX Cloud API.
* **Buy & Sell:** Trade stocks with validation (insufficient funds, invalid symbols).
* **Portfolio:** View current holdings, total value, and available cash.
* **History:** A detailed log of all transactions (symbol, price, shares, timestamp).

## 🛠️ Technology Stack
* **Backend:** Python (Flask), Jinja2 Templating
* **Database:** SQLite3 (`finance.db`)
* **Frontend:** HTML5, CSS3 (Custom styling from scratch), JavaScript
* **API:** IEX Cloud (for real-time financial data)

## 📂 File Structure
* `app.py` - The main controller. Handles all routes (`/buy`, `/sell`, `/login`, etc.) and database logic.
* `helpers.py` - Utility functions for checking login status (`@login_required`), formatting currency (`usd`), and querying the IEX API (`lookup`).
* `finance.db` - SQLite database storing tables for `users`, `transactions`, and `portfolio`.
* `templates/` - HTML files using Jinja syntax to render dynamic data.
* `static/` - Stylesheets (`styles.css`) and favicon.

## 📸 How to Run
1. Navigate to the project directory.
2. Export your API Key:
   ```bash
   export API_KEY=value
3. Run the Flask Application:
   ```bash
   flask run
4. Open the provided URL in your browser.

Developed for Harvard's CS50x Course.
    
