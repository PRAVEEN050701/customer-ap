import os
from flask import Flask, jsonify, request
import mysql.connector
import os
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# =========================
# APPLICATION CONFIGURATION
# =========================

APP_ENV = os.getenv("APP_ENV", "UNKNOWN")
APP_VERSION = os.getenv("APP_VERSION", "UNKNOWN")

# =========================
# DATABASE CONFIGURATION
# =========================

DB_HOST = os.getenv("DB_HOST", "customer-db")
DB_USER = os.getenv("DB_USER", "customer")
DB_PASSWORD = os.getenv("DB_PASSWORD", "customer123")
DB_NAME = os.getenv("DB_NAME", "customerdb")


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return jsonify({
        "application": "customer-app",
        "environment": APP_ENV,
        "version": APP_VERSION
    })


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "environment": APP_ENV,
        "version": APP_VERSION
    })


# =========================
# DATABASE TEST
# =========================

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


# =========================
# CUSTOMER SEARCH FEATURE
# =========================

@app.route("/customers/search")
def search_customers():

    name = request.args.get("name")

    # Validate search input
    if not name:
        return jsonify({
            "error": "Please provide a customer name"
        }), 400

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, name, email
            FROM customers
            WHERE name LIKE %s
        """

        search_value = "%" + name + "%"

        cursor.execute(query, (search_value,))
        customers = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({
            "search": name,
            "count": len(customers),
            "customers": customers
        })

    except Exception as e:
        return jsonify({
            "error": "Database search failed",
            "details": str(e)
        }), 500


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)