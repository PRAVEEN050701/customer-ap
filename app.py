import os
from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "UNKNOWN")
APP_VERSION = os.getenv("APP_VERSION", "UNKNOWN")

DB_HOST = os.getenv("DB_HOST", "customer-db")
DB_USER = os.getenv("DB_USER", "customer")
DB_PASSWORD = os.getenv("DB_PASSWORD", "customer123")
DB_NAME = os.getenv("DB_NAME", "customerdb")


@app.route("/")
def home():
    return jsonify({
        "application": "customer-app",
        "environment": APP_ENV,
        "version": APP_VERSION
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "environment": APP_ENV,
        "version": APP_VERSION
    })


@app.route("/db-test")
def db_test():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "database": "CONNECTED",
            "db_host": DB_HOST,
            "result": result[0]
        })

    except Exception as e:
        return jsonify({
            "database": "NOT CONNECTED",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)