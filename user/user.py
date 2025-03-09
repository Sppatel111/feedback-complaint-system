import psycopg2
from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LoginForm
from  dotenv import load_dotenv
import os
user = Blueprint("user", __name__, template_folder="templates", static_folder="static")

#Database Connection
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

@user.route('/', methods=['GET', 'POST'])
@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT password FROM user_auth WHERE email = %s", (email,))
                stored_password = cur.fetchone()

                if stored_password and password == stored_password[0]:
                    flash(f'Login successful for {email}', 'success')
                    return redirect(url_for("user.u_dashboard"))

        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('user.login'))

    return render_template('user_login.html', form=form)

@user.route('/dashboard')
def u_dashboard():
    return render_template("user_dashboard.html")

@user.route('/dashboard/settings')
def u_settings():
    return render_template("user_settings.html")
