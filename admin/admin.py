import psycopg2
from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LoginForm,UserRegistrationForm
from dotenv import load_dotenv
import os

load_dotenv()
admin = Blueprint("admin", __name__, template_folder="templates")

try:
    conn = psycopg2.connect(
        host=os.environ.get('HOST'),
        database=os.environ.get('DATABASE'),
        user=os.environ.get('USER'),
        password=os.environ.get('PASSWORD')
    )
except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")
    conn = None

# @admin.route('/')
# def admin1():
#     return "hello admin"

@admin.route('/', methods=['GET', 'POST'])
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password FROM admin_auth WHERE email = %s", (email,))
                stored_password = cur.fetchone()

                if stored_password and password == stored_password[0]:
                    flash(f'Login successful for {email}', 'success')
                    return redirect(url_for('admin.admin_dashboard'))

        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('admin.login'))

    return render_template('admin_login.html', form=form)

@admin.route('/dashboard')
def admin_dashboard():
    print("admin dashboard")
    return render_template("dashboard.html")

@admin.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserRegistrationForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO user_auth (email, password) VALUES (%s, %s)", (email, password))
                    conn.commit()
                    flash("User registered successfully!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {str(e)}", "danger")

        return redirect(url_for("admin.admin_dashboard"))

    return render_template("register_user.html", form=form)