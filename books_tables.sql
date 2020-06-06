
CREATE TABLE cs50_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL
);

CREATE TABLE cs50_books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE cs50_reviews (
    id SERIAL PRIMARY KEY,
    review_text VARCHAR NOT NULL,
    review_score INTEGER NOT NULL,
    books_id INTEGER REFERENCES cs50_books,
    users_id INTEGER REFERENCES cs50_users
);
