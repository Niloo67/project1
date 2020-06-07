# Project 1


The application allows users to register an account(hashed password) login, logout, search for books, leave a review (only1) for  books, and see reviews made by other people.
There is a book page where once you've selected a book you see book details and goodreads details about the book. On that same page you can rate and write a review(must do both) for the book and see other users' reviews.
You can submit a review and have it appear but once you have submitted a review.
 he application lets users to see book information and reviews made by other people using the Goodreads API.


first:
Set api_key environment variable to your Goodreads API key.
Set secret_key environment variable to your Flask secret key.
Set DATABASE_URL environment variable to the address of your Heroku database.
FLASK_APP environment is set to application.py, execute flask run to

All files stored within the project1 directory:
CSS and images are in static directory.HTML files are in the templates directory.
Website Flask / Python code stored within application.py.
books_tables: SQL code for three database tables.
books.csv: CSV file of 5000 books
import.py: is where I used Python code to upload CSV file contents (books info given) to a database table.
API/ isbn gives you the details of book in json format.

I used adminer for this project and all the user/hashed password are saved in a table, all reviews are saved on a different table and all book info from csv file are saved in another table.

To view a book's details in JSON format, navigate to .../api/ISBN_NUMBER. JSON returns data in the following format:

{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
