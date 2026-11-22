from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
app = Flask(__name__)


app.secret_key = os.environ.get("SECRET_KEY")


# =========================
# MYSQL CONNECTION
# =========================
#=============================
#def get_db_connection():
 #   return mysql.connector.connect(
  #      host="localhost",
   #     user="root",
    #    password="12345678",
     #   database="fake_product_detection"
   # )
#===========================



#   DAABASE CONNECTION
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "fake_product_detection"),
        port=int(os.environ.get("DB_PORT", 3306))
    )



# =========================
# PUBLIC / USER PAGES
# =========================


# Logo Page
@app.route("/")
def logo():
    return render_template("logo.html")


# Home Page
@app.route("/home")
def home():
    return render_template("index.html")

# Verify Product Page
#@app.route("/verify")
#def verify():
#    return render_template("verify.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():

    result = None

    if request.method == "POST":

        product_id = request.form["product_id"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT product_id, product_name
            FROM products
            WHERE product_id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        cursor.close()
        connection.close()

        if product:

            result = {
                "status": "Genuine",
                "product_id": product["product_id"],
                "product_name": product["product_name"]
            }

        else:

            result = {
                "status": "Not Verified"
            }

    return render_template(
        "verify.html",
        result=result
    )


# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Login Page
@app.route("/login")
def login():
    return render_template("login.html")


# Register Page
#@app.route("/register")
#def register():
 #   return render_template("register.html")
# Manufacturer Registration

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("Please fill all fields.")
            return redirect(url_for("register"))

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            # Check whether email already exists
            cursor.execute(
                "SELECT email FROM manufacturers WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already registered.")
                return redirect(url_for("register"))

            # Securely hash password
            hashed_password = generate_password_hash(password)

            # Save manufacturer details
            cursor.execute(
                """
                INSERT INTO manufacturers
                (name, email, password_hash)
                VALUES (%s, %s, %s)
                """,
                (name, email, hashed_password)
            )

            connection.commit()

            flash("Registration successful! Please login.")

            return redirect(url_for("manufacturer_login"))

        except mysql.connector.Error as error:

            connection.rollback()

            print("Registration Error:", error)

            flash("Registration failed. Please try again.")

        finally:
            cursor.close()
            connection.close()

    return render_template("register.html")




#=============================
# Manufacturer Pages
#===================================

# Manufacturer Login
#@app.route("/manufacturer_login")
#def manufacturer_login():
 #   return render_template("manufacturer_login.html")
# Manufacturer Login

@app.route("/manufacturer_login", methods=["GET", "POST"])
def manufacturer_login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please enter email and password.")
            return redirect(url_for("manufacturer_login"))

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            # Find manufacturer using email
            cursor.execute(
                """
                SELECT manufacturer_id, name, email, password_hash
                FROM manufacturers
                WHERE email = %s
                """,
                (email,)
            )

            manufacturer = cursor.fetchone()

            if manufacturer:

                # Check password
                if check_password_hash(
                    manufacturer[3], password
                ):

                    # Save login information in session
                    session["manufacturer_id"] = manufacturer[0]
                    session["manufacturer_name"] = manufacturer[1]
                    session["manufacturer_email"] = manufacturer[2]

                    flash("Login successful!")

                    return redirect(
                        url_for("manufacturer_dashboard")
                    )

            flash("Invalid email or password.")

        except mysql.connector.Error as error:

            print("Login Error:", error)

            flash("Database error occurred.")

        finally:
            cursor.close()
            connection.close()

    return render_template("manufacturer_login.html")



# Manufacturer Dashboard
#@app.route("/manufacturer-dashboard")
#def manufacturer_dashboard():
 #   return render_template("manufacturer_dashboard.html")


@app.route("/manufacturer-dashboard")
def manufacturer_dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT product_id, product_name
        FROM products
        ORDER BY product_id DESC
    """)

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "manufacturer_dashboard.html",
        products=products
    )

# =========================
# ADD PRODUCT
# =========================

# Add Product page
#@app.route("/add-product")
#def add_product():
 #   return render_template("add_product.html")

@app.route("/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        product_name = request.form["product_name"]
        product_id = request.form["product_id"]

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            # Check whether Product ID already exists
            cursor.execute(
                "SELECT product_id FROM products WHERE product_id = %s",
                (product_id,)
            )

            existing_product = cursor.fetchone()

            if existing_product:
                flash("Product ID already exists.")
                return redirect(url_for("add_product"))

            # Insert new product
            cursor.execute(
                """
                INSERT INTO products (product_id, product_name)
                VALUES (%s, %s)
                """,
                (product_id, product_name)
            )

            connection.commit()

            flash("Product added successfully!")

        except mysql.connector.Error as error:

            connection.rollback()

            flash("Database error occurred.")

            print("Database Error:", error)

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("add_product"))

    return render_template("add_product.html")



# =========================
# RUN APPLICATION
# =========================


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)