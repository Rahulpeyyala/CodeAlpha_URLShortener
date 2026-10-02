
from flask import Flask, request, jsonify, redirect, render_template
import sqlite3
import string
import random
import os

app = Flask(__name__)

DATABASE = "url_shortener.db"

# Create database
def init_db():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Generate unique short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits

    while True:
        code = ''.join(
            random.choice(characters)
            for _ in range(length)
        )

        connection = sqlite3.connect(DATABASE)

        result = connection.execute(
            "SELECT id FROM urls WHERE short_code = ?",
            (code,)
        ).fetchone()

        connection.close()

        if result is None:
            return code


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Shorten URL API
@app.route("/shorten", methods=["POST"])
def shorten_url():

    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({
            "error": "URL is required"
        }), 400

    original_url = data["url"]

    short_code = generate_short_code()

    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        INSERT INTO urls (original_url, short_code)
        VALUES (?, ?)
        """,
        (original_url, short_code)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "original_url": original_url,
        "short_code": short_code
    })


# Redirect short URL
@app.route("/<short_code>")
def redirect_to_original(short_code):

    connection = sqlite3.connect(DATABASE)

    result = connection.execute(
        """
        SELECT original_url
        FROM urls
        WHERE short_code = ?
        """,
        (short_code,)
    ).fetchone()

    connection.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
