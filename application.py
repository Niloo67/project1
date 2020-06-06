import os, json
from os import environ
# Flask imports
from flask import Flask, request, render_template, jsonify, session
from flask_session import Session
# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# Allows to send HTTP/1.1 requests using Python
import requests, sys
# password hashing
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Get Flask secret key
app.secret_key = "CVXW1Pt31K0PjZYWD6A40DcL0Xp3FNt6ZKKUE9T9Ls"


# Check for environment variable.
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    """register or log in."""

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Allows user to register."""

    if request.method == "GET":
        return render_template("register.html")

    # get username & password from 'register.html' form
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")

    # check for empty fields, passwords match & unique username
    if not username:
        return render_template("error.html", message="Must enter a username.")
    if not password:
        return render_template("error.html", message="Must enter a password.")
    if not password_confirm:
        return render_template("error.html", message="Must confirm your password.")
    if password != password_confirm:
        return render_template("error.html", message="Passwords do not match.")
    if db.execute("SELECT * FROM cs50_users WHERE username = :username", {"username": username}).rowcount > 0:
        return render_template("error.html", message="Username already exists.")

    # Hash password
    hashed_password = generate_password_hash(password)

    # Insert new user into 'cs50_users' table
    db.execute("INSERT INTO cs50_users (username, password_hash) VALUES (:username, :password_hash)", {
               "username": username, "password_hash": hashed_password})
    db.commit()

    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Allows user to log in."""

    if request.method == "GET":
        return render_template("login.html")

    # get username & password from 'login.html'
    username = request.form.get("username")
    password = request.form.get("password")

    # check for empty fields
    if not username:
        return render_template("error.html", message="Must enter a username.")
    if not password:
        return render_template("error.html", message="Must enter a password.")

    # Selects user from 'cs50_users' table& Check if user exists
    result = db.execute(
        "SELECT * FROM cs50_users WHERE username = :username", {"username": username}).fetchone()
    if not result:
        return render_template("error.html", message="Username not found.")

    # Checks password against hashed password value. Returns bool value.
    check = check_password_hash(result.password_hash, password)

    # Checks input password is equal to hashed password.
    if check is True:
        # Remembers which user logged in
        session["user_id"] = result.id
        return render_template("search.html")
    else:
        print("Username / password combination not found.", file=sys.stderr)
        return render_template("login.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    """Searches books in database."""

    if request.method == "GET":
        return render_template("search.html")

    # get search term from 'search.html' form and wrap in wildcard chars.
    search_term = request.form.get("search_term")
    search_term = '%' + search_term + '%'

    # Extract what field to search.
    search_field = request.form.get("search_field")

    if search_field == 'isbn':
        results = db.execute("SELECT * FROM cs50_books WHERE UPPER(isbn) LIKE UPPER(:search_term)", {
                             "search_term": search_term}).fetchall()
    elif search_field == 'title':
        results = db.execute("SELECT * FROM cs50_books WHERE upper(title) LIKE UPPER(:search_term)", {
                             "search_term": search_term}).fetchall()
    elif search_field == 'author':
        results = db.execute("SELECT * FROM cs50_books WHERE upper(author) LIKE UPPER(:search_term)", {
                             "search_term": search_term}).fetchall()
    elif search_field == 'all':
        # Search database. Cast year (int) to string for comparison.
        results = db.execute("SELECT * FROM cs50_books WHERE UPPER(isbn) LIKE UPPER(:search_term) OR UPPER(title) LIKE UPPER(:search_term) OR UPPER(author) LIKE UPPER(:search_term) OR CAST(year AS VARCHAR) LIKE :search_term", {
                             "search_term": search_term}).fetchall()

    # Track search result counts.
    counter = 0
    for result in results:
        counter = counter + 1
    # if no results found error message
    if counter == 0:
        return render_template("error.html", message="No results were found!")
    else:
        return render_template("results.html", results=results, counter=counter)


@app.route("/result/<isbn>")
def isbn(isbn):
    """Displays information (Goodreads and user-submitted reviews) about book."""

    # get book information and set 'book_id' session.
    result = db.execute(
        "SELECT * FROM cs50_books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    session["books_id"] = result.id

    # get all review information (if exists).
    reviews = db.execute("SELECT username, review_text, review_score FROM cs50_users JOIN cs50_reviews ON cs50_reviews.users_id = cs50_users.id WHERE books_id = :books_id", {
                         "books_id": result.id}).fetchall()
    if reviews:
        reviews_exist = True
    else:
        reviews_exist = False

    # get Goodreads information on book.
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "wKRYJQHIX0OIRmmTDZOsQ", "isbns": isbn})
    data = res.json()
    average_rating = data["books"][0]["average_rating"]
    work_ratings_count = data["books"][0]["work_ratings_count"]

    # check if user has previously submitted a review.
    review_status = db.execute("SELECT * FROM cs50_reviews WHERE users_id = :users_id AND books_id = :books_id", {
                               "users_id": session["user_id"], "books_id": result.id}).fetchone()

    if review_status:
        review_status = True
        return render_template("bookpage.html", result=result, rating=average_rating, num_reviews=work_ratings_count, reviews_exist=reviews_exist, review_status=review_status, reviews=reviews)
    else:
        review_status = False
        return render_template("bookpage.html", result=result, rating=average_rating, num_reviews=work_ratings_count, reviews_exist=reviews_exist, review_status=review_status, reviews=reviews)


@app.route("/result/<isbn>", methods=["POST"])
def review(isbn):
    """Insert user submitted book score and review to database."""

    # get user-submitted score and review.
    review_text = request.form.get("review_text")
    review_score = request.form.get("review_score")

    if not review_text or not review_score:
        return render_template("error.html", message="Please Rate and Review book.")

    # Insert into 'cs50_reviews' table
    db.execute("INSERT INTO cs50_reviews (review_text, review_score, books_id, users_id) VALUES (:review_text, :review_score, :books_id, :users_id)", {
               "review_text": review_text, "review_score": review_score, "books_id": session["books_id"], "users_id": session["user_id"]})
    db.commit()

    # Forget 'books_id' session.
    session.pop('books_id')

    return render_template("submitted.html", review_text=review_text, review_score=review_score, isbn=isbn)


@app.route("/logout")
def logout():
    """Logs user out."""

    # Forget 'user_id' session.
    session.pop('user_id')

    return render_template("logout.html")


@app.route("/api/<isbn>")
def api(isbn):
    """Application API."""

    # get information from database.
    result = db.execute(
        "SELECT * FROM cs50_books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # Error-check.
    if result is None:
        return jsonify({
            "message": "error - Book not in database."
        })

    # get information from Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "wKRYJQHIX0OIRmmTDZOsQ", "isbns": isbn})
    data = res.json()
    average_rating = data["books"][0]["average_rating"]
    work_ratings_count = data["books"][0]["work_ratings_count"]

    # Return jsonify'd information.
    return jsonify({
        "title": result.title,
        "author": result.author,
        "year": result.year,
        "isbn": result.isbn,
        "review_count": work_ratings_count,
        "average_score": average_rating
    })


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html', message="404 - page not found"), 404
